import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from emotiongsr import DataProcessor
import webbrowser
import tempfile
import os
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')


def run_app(root):
    root.title("Emotion Heatmap Generator")

    # Layout for directory selection
    ttk.Label(root, text="IMOTIONS_PATH:").grid(row=0, column=0)
    imotions_path_entry = ttk.Entry(root)
    imotions_path_entry.grid(row=0, column=1)
    ttk.Button(root, text="Browse", command=lambda: select_directory(imotions_path_entry)).grid(row=0, column=2)

    ttk.Label(root, text="IMAGES_PATH:").grid(row=1, column=0)
    images_path_entry = ttk.Entry(root)
    images_path_entry.grid(row=1, column=1)
    ttk.Button(root, text="Browse", command=lambda: select_directory(images_path_entry)).grid(row=1, column=2)

    ttk.Label(root, text="OUTPUT_PATH:").grid(row=2, column=0)
    output_path_entry = ttk.Entry(root)
    output_path_entry.grid(row=2, column=1)
    ttk.Button(root, text="Browse", command=lambda: select_directory(output_path_entry)).grid(row=2, column=2)

    # Emotion and signal selection
    ttk.Label(root, text="Select Emotion:").grid(row=3, column=0)
    emotion_combobox = ttk.Combobox(root, values=[
        "All Emotions",  # "All Emotions" is a special value to generate a heatmap for all emotions
    "Anger",
    "Contempt",
    "Disgust",
    "Fear",
    "Joy",
    "Sadness",
    "Surprise",
    "Engagement",
    "Valence",
    "Sentimentality",
    "Confusion",
    "Neutral",
])
    emotion_combobox.grid(row=3, column=1, columnspan=2)
    emotion_combobox.current(0)

    ttk.Label(root, text="Select Signal:").grid(row=4, column=0)
    signal_combobox = ttk.Combobox(root, values=["GSR Raw","Phasic Signal", "Tonic Signal","Emotion intensity"])
    signal_combobox.grid(row=4, column=1, columnspan=2)
    signal_combobox.current(0)
    plot_frame = ttk.Frame(root)
    plot_frame.grid(row=6, column=0, columnspan=3, sticky='nsew')
    def select_directory(entry_field):
        directory = filedialog.askdirectory()
        entry_field.delete(0, tk.END)
        entry_field.insert(0, directory)

    def display_matplotlib_figure(fig):
        # Clear the previous plot
        for widget in plot_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def display_plotly_figure(fig):
        # Clear the previous plot
        for widget in plot_frame.winfo_children():
            widget.destroy()

        # Save Plotly figure as an HTML file and open it in a web view
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        fig.write_html(temp_file.name)
        webbrowser.open('file://' + temp_file.name)

    def display_multiple_plotly_figure(figs):
        # Clear the previous plot
        for widget in plot_frame.winfo_children():
            widget.destroy()

        # Save Plotly figure as an HTML file and open it in a web view
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        with open(temp_file.name, 'w') as f:
            for figure in figs:
                f.write(figure.to_html(full_html=False, include_plotlyjs='cdn'))
                f.write("<br>")
        
        webbrowser.open('file://' + temp_file.name)

    def generate_heatmap():
        IMOTIONS_PATH = imotions_path_entry.get()
        IMAGES_PATH = images_path_entry.get()
        OUTPUT_PATH = output_path_entry.get()

        if not (IMOTIONS_PATH and IMAGES_PATH and OUTPUT_PATH):
            messagebox.showerror("Error", "Please select all directories.")
            return

        processor = DataProcessor(IMOTIONS_PATH, IMAGES_PATH, OUTPUT_PATH)
        processor.clean_files()
        data = processor.get_clean_data()

        emotion = emotion_combobox.get()
        signal = signal_combobox.get()
        if emotion and signal:
            try:
                # Assuming an image path is required for heatmap generation
                IMAGE_PATH = filedialog.askopenfilename(title="Select Image File", filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")])
                if not IMAGE_PATH:
                    raise Exception("No image selected")
                
                if signal == "Emotion intensity":
                    # matplotlib show within the window
                    matrix_like_object = processor.generate_heatmap(data, emotion, IMAGE_PATH)

                    # Plotting the matrix-like object
                    fig, ax = plt.subplots()  # Create a figure and axis to plot
                    ax.imshow(matrix_like_object)  # Show the image
                    ax.axis('off')  # Hide the axis
                    display_matplotlib_figure(fig) 
                #all emotions case
                elif emotion == "All Emotions":
                    figs = processor.get_all_emotion_heatmaps(data, signal, IMAGE_PATH)
                    display_multiple_plotly_figure(figs)                   
                else:
                    fig = processor.generate_emotion_heatmap(data, emotion, signal, IMAGE_PATH)
                    display_plotly_figure(fig)
                
                
                messagebox.showinfo("Success", "Heatmap generated successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    ttk.Button(root, text="Generate Heatmap", command=generate_heatmap).grid(row=5, column=0, columnspan=3)

    for i in range(6):
        root.grid_columnconfigure(i, weight=1)

