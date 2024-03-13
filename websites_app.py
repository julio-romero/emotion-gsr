import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Label, Button, Frame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from multimotions.dataprocessor import DataProcessor

def run_web_app(root):
    root.title("Website Heatmap Experiment")

    def select_file(entry):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if filepath:
            entry.delete(0, tk.END)
            entry.insert(0, filepath)

    def select_directory(entry):
        directory = filedialog.askdirectory()
        if directory:
            entry.delete(0, tk.END)
            entry.insert(0, directory)

    def generate_heatmap():
        imotions_csv = imotions_entry.get()
        scroll_csv = scroll_entry.get()
        output_path = output_path_entry.get()

        if not imotions_csv or not scroll_csv or not output_path:
            messagebox.showerror("Error", "Please select all required files and output directory")
            return

        processor = DataProcessor(scroll_csv, imotions_csv, output_path)
        processor.process_data()
        fig = processor.plot_heatmap()

        # Display the figure in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # File selection UI
    frame = Frame(root)
    frame.pack(pady=20)

    Label(frame, text="IMOTIONS_CSV:").grid(row=0, column=0, padx=5, pady=5)
    imotions_entry = tk.Entry(frame)
    imotions_entry.grid(row=0, column=1, padx=5, pady=5)
    Button(frame, text="Browse", command=lambda: select_file(imotions_entry)).grid(row=0, column=2, padx=5, pady=5)

    Label(frame, text="SCROLL_CSV:").grid(row=1, column=0, padx=5, pady=5)
    scroll_entry = tk.Entry(frame)
    scroll_entry.grid(row=1, column=1, padx=5, pady=5)
    Button(frame, text="Browse", command=lambda: select_file(scroll_entry)).grid(row=1, column=2, padx=5, pady=5)

    Label(frame, text="OUTPUT_PATH:").grid(row=2, column=0, padx=5, pady=5)
    output_path_entry = tk.Entry(frame)
    output_path_entry.grid(row=2, column=1, padx=5, pady=5)
    Button(frame, text="Browse", command=lambda: select_directory(output_path_entry)).grid(row=2, column=2, padx=5, pady=5)

    Button(root, text="Generate Heatmap", command=generate_heatmap).pack(pady=10)

    # Frame for plotting
    plot_frame = Frame(root)
    plot_frame.pack(fill=tk.BOTH, expand=True)


