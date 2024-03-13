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
from tkinter import ttk
from Experiment_Peaks_Controller import VideoProcessingApp
from Experiment_Web_Controller import *
from images_app import run_app
import tkinter as tk
from tkinter import ttk

class ExperimentManagementGUI:
    def __init__(self, master):
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        # Configure the root window
        self.master.title("Experiment Management")
        self.master.state('zoomed')  # Maximized window

        # Create a title label
        self.title = tk.Label(self.master, text="Experiment Management", font=("Helvetica", 24))
        self.title.pack(pady=20)

        # Create buttons
        self.button1 = tk.Button(self.master, text="Website Experiment", command=self.website_experiment)
        self.button1.place(relx=0.5, rely=0.45, anchor='center')

        self.button2 = tk.Button(self.master, text="Video Experiment", command=self.video_experiment)
        self.button2.place(relx=0.5, rely=0.55, anchor='center')

        self.button3 = tk.Button(self.master, text="Image Experiment", command=self.image_experiment)
        self.button3.place(relx=0.5, rely=0.65, anchor='center')

    # Define methods for each experiment type
    def website_experiment(self):
        print("Website experiment selected")
        
        #********************************************** GUI *********************************************************
        self.master.state('zoomed')
        self.master.withdraw()
        root = tk.Toplevel()

        # Create three frames
        frame1 = tk.Frame(root)
        frame1.pack(side='top', fill='both', expand=True)

        frame2 = tk.Frame(root)
        frame2.pack(side='top', fill='both', expand=True)

        frame3 = tk.Frame(root)
        frame3.pack(side='bottom', fill='both', expand=True)

        frame4 = tk.Frame(root) # Frame 4 for viewing past results
        results_frame = tk.Frame(frame4)
        results_frame.grid(row=4, column=0, columnspan=2)
        # function to load the web data 
        def load_file1():
            file_path1.set(filedialog.askopenfilename())

        # function to load the emotion data
        def load_file2():
            file_path2.set(filedialog.askopenfilename())

        # function to process the code and show the results 
        def process():
            start_time = time.time() # set a timer for the process 

            # Validation checks, to check the user choose the right selections and show a massages for wrong selection
            if experiment_mode.get() == "new" and not new_experiment_name.get().strip():
                tk.messagebox.showerror("Error", "Please enter a name for the new experiment!")
                return
            elif experiment_mode.get() == "existing" and not existing_experiment_name.get():
                tk.messagebox.showerror("Error", "Please select an existing experiment!")
                return
            
            if not username.get():
                messagebox.showerror("Error", "Please enter a username.")
                return
            
            if not file_path1.get():
                messagebox.showerror("Error", "Please select web data CSV file.")
                return
            
            if not file_path2.get():
                messagebox.showerror("Error", "Please select emotion data CSVfiles.")
                return

            # Create a directory for the experiment, then for the user
            base_dir = "experiments_website" # Base directory for experiments
            
            if experiment_mode.get() == "new":
                # creating a new experiment directory
                experiment_dir = os.path.join(base_dir, new_experiment_name.get())
            else:
                # using an existing experiment directory
                experiment_dir = os.path.join(base_dir, existing_experiment_name.get())

            # Create or get the directory for the user within the experiment directory
            user_dir = os.path.join(experiment_dir, username.get())
            os.makedirs(user_dir, exist_ok=True)

            # call the function to process the data
            image_paths = process_files(file_path1.get(), file_path2.get(), user_dir)

            # call the function to display the results 
            display_images(image_paths, frame3)
            end_time = time.time()
            duration = end_time - start_time
            timer_value.set(f"Time elapsed: {duration} seconds")
            root.update()

        # function to show the results while asking for previous history 
        def show_results_frame():
            # Switch to results frame.
            frame1.pack_forget()
            frame2.pack_forget()
            frame3.pack_forget()
            frame4.pack(fill='both', expand=True)

        # function to go back to the main frame 
        def show_main_frame():
            # Switch back to the main frame.
            frame4.pack_forget()
            frame1.pack(side='top', fill='both', expand=True)
            frame2.pack(side='top', fill='both', expand=True)
            frame3.pack(side='bottom', fill='both', expand=True)

        # function to update the users with the expriment selected 
        def update_user_dropdown(*args):
            # Update the user dropdown based on the selected experiment.
            selected_experiment = existing_experiment_dropdown_results.get()
            user_directory = os.path.join("experiments_website", selected_experiment)
            
            # Check if it's a directory and get all subdirectories (users) within it
            if os.path.isdir(user_directory):
                users = [name for name in os.listdir(user_directory) if os.path.isdir(os.path.join(user_directory, name))]
                user_dropdown_results['values'] = users
            else:
                user_dropdown_results['values'] = []


        # function to display rhe previous results 
        def display_past_results():
            # Get the chosen experiment and user
            selected_experiment = existing_experiment_dropdown_results.get()
            selected_user = user_dropdown_results.get()

            if not selected_experiment or not selected_user:
                messagebox.showerror("Error", "Please select both experiment and user.")
                return
            
            # Define the directory path
            base_path = os.path.join("experiments_website", selected_experiment, selected_user, "output_scatter_full_web_images")

            # Get all the URL subfolders
            url_folders = [folder for folder in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, folder))]

            image_paths = []
            for url_folder in url_folders:
                # Find the heatmap image in each URL subfolder
                image_file = os.path.join(base_path, url_folder, 'heatmap_webpage_screenshot.png')
                if os.path.exists(image_file):
                    image_paths.append(image_file)

            # Use the display_images function to show the heatmaps
            display_images(image_paths, None, results_frame)

        #***************************** GUI Design *********************************************    


        # Define string variables
        username = tk.StringVar()
        file_path1 = tk.StringVar()
        file_path2 = tk.StringVar()

        # Radio button to choose between existing or new experiment
        experiment_mode = tk.StringVar(value="new")
        radio1 = tk.Radiobutton(frame1, text="Add to existing experiment", variable=experiment_mode, value="existing")
        radio2 = tk.Radiobutton(frame1, text="Create new experiment", variable=experiment_mode, value="new")
        radio1.grid(row=2, column=0)
        radio2.grid(row=2, column=2)

        # Entry for new experiment name
        new_experiment_name = tk.StringVar()
        new_experiment_entry = tk.Entry(frame1, textvariable=new_experiment_name)
        new_experiment_entry.grid(row=2, column=4)
        new_experiment_label = tk.Label(frame1, text="New Experiment Name")
        new_experiment_label.grid(row=2, column=3)

        # Ensure the experiments directory exists
        if not os.path.exists("experiments_website"):
            os.makedirs("experiments_website")

        # Drop-down menu for existing experiments
        existing_experiments = [name for name in os.listdir("experiments_website") if os.path.isdir(os.path.join("experiments_website", name))]
        existing_experiment_name = tk.StringVar()
        existing_experiment_dropdown = ttk.Combobox(frame1, textvariable=existing_experiment_name)
        existing_experiment_dropdown['values'] = existing_experiments
        existing_experiment_dropdown.grid(row=4, column=1)

        existing_experiment_label = tk.Label(frame1, text="Existing Experiments")
        existing_experiment_label.grid(row=4, column=0)

        # Define a string variable to hold the timer value
        timer_value = tk.StringVar()
        timer_value.set("Time elapsed: 0 seconds")

        # Create a label to display the timer value
        timer_label = tk.Label(frame1, textvariable=timer_value)
        timer_label.grid(row=7, column=2)

        # Bind the username variable to the Entry widget
        username_label = tk.Label(frame1, text="Username")
        username_label.grid(row=5, column=0)

        username_entry = tk.Entry(frame1, textvariable=username)
        username_entry.grid(row=5, column=1)

        # Bind the file path variables to the Entry widgets
        entry1 = tk.Entry(frame1, textvariable=file_path1)
        entry1.grid(row=6, column=1)

        entry2 = tk.Entry(frame1, textvariable=file_path2)
        entry2.grid(row=7, column=1)

        # Define the buttons
        button1 = tk.Button(frame1, text="Load Web Data", command=load_file1)
        button1.grid(row=6, column=0)

        button2 = tk.Button(frame1, text="Load Emotion Data", command=load_file2)
        button2.grid(row=7, column=0)

        process_button = tk.Button(frame1, text="Process Files", command=process)
        process_button.grid(row=6, column=2, columnspan=2)


        # Drop-down menu for existing experiments on the results page
        existing_experiment_dropdown_results = ttk.Combobox(frame4, textvariable=existing_experiment_name)
        existing_experiment_dropdown_results['values'] = existing_experiments
        existing_experiment_dropdown_results.grid(row=0, column=1)

        existing_experiment_label_results = tk.Label(frame4, text="Existing Experiments")
        existing_experiment_label_results.grid(row=0, column=0)

        # Bind the update function to the existing_experiment_name variable
        existing_experiment_name.trace_add("write", update_user_dropdown)

        # Drop-down menu for existing users within the selected experiment on the results page
        selected_user_results = tk.StringVar()
        user_dropdown_results = ttk.Combobox(frame4, textvariable=selected_user_results)
        user_dropdown_results.grid(row=1, column=1)

        user_label_results = tk.Label(frame4, text="User")
        user_label_results.grid(row=1, column=0)

        # Button to load and display results for the selected experiment and user
        load_results_button = tk.Button(frame4, text="Load Results", command=display_past_results)
        load_results_button.grid(row=2, column=0, columnspan=2)

        # Back button on the results page
        back_button = tk.Button(frame4, text="Back to Main", command=show_main_frame)
        back_button.grid(row=3, column=0, columnspan=2)

        # Button to switch to the results frame from the main frame
        switch_to_results_button = tk.Button(frame1, text="View Previous Results", command=show_results_frame)
        switch_to_results_button.grid(row=6, column=4)
        def on_toplevel_close():
            self.master.deiconify()
            self.master.state('zoomed')# Show the main window
            root.destroy()  # Destroy the Toplevel window

        root.protocol("WM_DELETE_WINDOW", on_toplevel_close)  # Define close behavior
        root.mainloop()

    def video_experiment(self):
        # Create the main window
        print("Video experiment selected")
        self.master.state('zoomed')
        self.master.withdraw()
        root = tk.Toplevel()
        app = VideoProcessingApp(root)
        
        
        def on_toplevel_close():
            self.master.deiconify()
            self.master.state('zoomed')# Show the main window
            root.destroy()  # Destroy the Toplevel window

        root.protocol("WM_DELETE_WINDOW", on_toplevel_close)  # Define close behavior
        root.mainloop()

    def image_experiment(self):
        print("Image experiment selected")
        self.master.state('zoomed')
        self.master.withdraw()
        root = tk.Toplevel()
        run_app(root)
        def on_toplevel_close():
            self.master.deiconify()
            self.master.state('zoomed')# Show the main window
            root.destroy()  # Destroy the Toplevel window

        root.protocol("WM_DELETE_WINDOW", on_toplevel_close)  # Define close behavior
        root.mainloop()
        
        


def main():
    root = tk.Tk()
    app = ExperimentManagementGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
