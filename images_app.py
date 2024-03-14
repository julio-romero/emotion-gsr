"""
images_app.py

This module contains the GUI for Priyanks experiment


"""

import tempfile
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from emotiongsr import DataProcessor

matplotlib.use("TkAgg")

EMOTIONS = [
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
]

def run_app(root):
    """Main method called from the application entry point to run the GUI."""
    root.title("Emotion Heatmap Generator")

    # Layout for directory selection
    ttk.Label(root, text="IMOTIONS_PATH:").grid(row=0, column=0)
    imotions_path_entry = ttk.Entry(root)
    imotions_path_entry.grid(row=0, column=1)
    ttk.Button(
        root, text="Browse", command=lambda: select_directory(imotions_path_entry)
    ).grid(row=0, column=2)

    ttk.Label(root, text="OUTPUT_PATH:").grid(row=1, column=0)
    output_path_entry = ttk.Entry(root)
    output_path_entry.grid(row=1, column=1)
    ttk.Button(
        root, text="Browse", command=lambda: select_directory(output_path_entry)
    ).grid(row=1, column=2)

    # Emotion and signal selection
    ttk.Label(root, text="Select Emotion:").grid(row=3, column=0)
    emotion_combobox = ttk.Combobox(
        root,
        values=[
            "All Emotions",  # Special value to generate a heatmap for all emotions
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
        ],
    )
    emotion_combobox.grid(row=3, column=1, columnspan=2)
    emotion_combobox.current(0)

    ttk.Label(root, text="Select Signal:").grid(row=4, column=0)
    signal_combobox = ttk.Combobox(
        root, values=["GSR Raw", "Phasic Signal", "Tonic Signal", "Emotion intensity"]
    )
    signal_combobox.grid(row=4, column=1, columnspan=2)
    signal_combobox.current(0)
    plot_frame = ttk.Frame(root)
    plot_frame.grid(row=6, column=0, columnspan=3, sticky="nsew")

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
        webbrowser.open("file://" + temp_file.name)

    def display_multiple_plotly_figure(figs):
        # Clear the previous plot
        for widget in plot_frame.winfo_children():
            widget.destroy()

        # Save Plotly figure as an HTML file and open it in a web view
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        with open(temp_file.name, "w", encoding="utf-8") as f:
            for figure in figs:
                f.write(figure.to_html(full_html=False, include_plotlyjs="cdn"))
                f.write("<br>")

        webbrowser.open("file://" + temp_file.name)

    def generate_heatmap():
        imotions_path = imotions_path_entry.get()

        output_path = output_path_entry.get()

        processor = DataProcessor(imotions_path, output_path)
        processor.clean_files()
        data = processor.get_clean_data()

        emotion = emotion_combobox.get()
        signal = signal_combobox.get()
        if emotion and signal:
            try:
                # Assuming an image path is required for heatmap generation
                image_path = filedialog.askopenfilename(
                    title="Select Image File",
                    filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")],
                )
                if not image_path:
                    raise ValueError("Image file not selected.")

                if signal == "Emotion intensity" and not emotion == "All Emotions":
                    # matplotlib show within the window
                    matrix_like_object = processor.generate_heatmap(
                        data, emotion, image_path
                    )

                    # Plotting the matrix-like object
                    fig, ax = plt.subplots()  # Create a figure and axis to plot
                    ax.imshow(matrix_like_object)  # Show the image
                    ax.axis("off")  # Hide the axis
                    display_matplotlib_figure(fig)
                elif signal == "Emotion intensity" and emotion == "All Emotions":
                    # matplotlib show within the window
                    fig, ax = plt.subplots(3, 4, figsize=(75, 100))
                    for emotion in EMOTIONS:
                        matrix_like_object = processor.generate_heatmap(
                            data, emotion, image_path
                        )
                        ax[EMOTIONS.index(emotion) // 4][EMOTIONS.index(emotion) % 4].imshow(
                            matrix_like_object
                        )
                        ax[EMOTIONS.index(emotion) // 4][EMOTIONS.index(emotion) % 4].axis(
                            "off"
                        )
                        # label the subplots
                        ax[EMOTIONS.index(emotion) // 4][EMOTIONS.index(emotion) % 4].set_title(
                            emotion, fontsize=10
                        )
                        
                    # Display figure on a separate window
                    plt.show()
                # all emotions case
                elif emotion == "All Emotions":
                    figs = processor.get_all_emotion_heatmaps(data, signal, image_path)
                    display_multiple_plotly_figure(figs)
                else:
                    fig = processor.generate_emotion_heatmap(
                        data, emotion, signal, image_path
                    )
                    display_plotly_figure(fig)

                messagebox.showinfo("Success", "Heatmap generated successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    ttk.Button(root, text="Generate Heatmap", command=generate_heatmap).grid(
        row=5, column=0, columnspan=3
    )

    for i in range(6):
        root.grid_columnconfigure(i, weight=1)
