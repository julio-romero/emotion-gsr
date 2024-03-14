"""
app.py

This application serves as a processor for iMotions data 
and neuromarketing experiments; its built on top of Sajeda's code along
with Mohammad's and Priyank's code.

Current functionalities are:
    - Web Emotion Analysis (from Mohamad's code)
    - Image Emotion Analysis (from Priyank's code)
    - Video Emotion Analysis (from Sajeda's code)

The code purpose its to demonstrate the capabilities of the three
different approaches to emotion analysis and how they can be used
for further analysis and insights.

13th of March, 2024

Colchester, UK

Authors:
    - Lesly C Guerrero Velez 
    - Manuel J Romero Olvera
    - Add yourself here
"""
import tkinter as tk
from Experiment_Peaks_Controller import VideoProcessingApp
from images_app import run_app
from websites_app import run_web_app


class ExperimentManagementGUI:
    """
    Main class for the GUI
    """

    def __init__(self, master):
        """
        Initialize the main window
        """
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for each experiment"""
        # Configure the root window
        self.master.title("Experiment Management")
        self.master.state("zoomed")  # Maximized window

        # Create a title label
        self.title = tk.Label(
            self.master, text="Experiment Management", font=("Helvetica", 24)
        )
        self.title.pack(pady=20)

        # Create buttons
        self.button1 = tk.Button(
            self.master, text="Website Experiment", command=self.website_experiment
        )
        self.button1.place(relx=0.5, rely=0.45, anchor="center")

        self.button2 = tk.Button(
            self.master, text="Video Experiment", command=self.video_experiment
        )
        self.button2.place(relx=0.5, rely=0.55, anchor="center")

        self.button3 = tk.Button(
            self.master, text="Image Experiment", command=self.image_experiment
        )
        self.button3.place(relx=0.5, rely=0.65, anchor="center")

    # Define methods for each experiment type
    def website_experiment(self):
        """Call the website experiment from Mohammad's code"""
        print("Website experiment selected")
        self.master.state("zoomed")
        self.master.withdraw()
        root = tk.Toplevel()
        run_web_app(root)

        def on_toplevel_close():
            self.master.deiconify()
            self.master.state("zoomed")  # Show the main window
            root.destroy()  # Destroy the Toplevel window

        root.protocol("WM_DELETE_WINDOW", on_toplevel_close)  # Define close behavior
        root.mainloop()

    def video_experiment(self):
        """Call the video experiment from Sajeda's code"""
        # Create the main window
        print("Video experiment selected")
        self.master.state("zoomed")
        self.master.withdraw()
        root = tk.Toplevel()
        app = VideoProcessingApp(root)

        def on_toplevel_close():
            self.master.deiconify()
            self.master.state("zoomed")  # Show the main window
            root.destroy()  # Destroy the Toplevel window

        root.protocol("WM_DELETE_WINDOW", on_toplevel_close)  # Define close behavior
        root.mainloop()

    def image_experiment(self):
        """Call the image experiment from Priyank's code"""
        print("Image experiment selected")
        self.master.state("zoomed")
        self.master.withdraw()
        root = tk.Toplevel()
        run_app(root)

        def on_toplevel_close():
            self.master.deiconify()
            self.master.state("zoomed")  # Show the main window
            root.destroy()  # Destroy the Toplevel window

        root.protocol("WM_DELETE_WINDOW", on_toplevel_close)  # Define close behavior
        root.mainloop()


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = ExperimentManagementGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
