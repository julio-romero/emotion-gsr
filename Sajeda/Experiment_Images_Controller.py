import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from openpyxl import Workbook
import os
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
from PIL import Image, ImageTk


# Declare figs list in the global scope
figs = []
plot_index = 0
plot_queue = deque()
plot_window = None
canvas = None
base_dir = "Output"
seen_plots = [] # Images that were already displayed
pending_plots = []  # Images in the queue to be displayed

def run_app(root):

    # Step 1 For Cleaning Csv
    def file_clean(df, filename):
        df = df[df[df[0] == "Row"].index[0]:]
        df = df.reset_index(drop=True)
        df.columns = df.iloc[0].tolist()
        df = df[1:]
        df["SlideEvent"] = df["SlideEvent"].ffill()
        df = df.loc[df.SlideEvent == "StartMedia"]
        df = df.drop(["EventSource", "GSR Resistance CAL", "GSR Conductance CAL", "Heart Rate PPG ALG"], axis=1)
        df = df.reset_index(drop=True)
        df["Participant"] = filename
        return df

    def clean_files(raw_path, output_path):
        columns_to_keep = ['Timestamp', 'Row', 'StimType', 'Duration', 'SourceStimuliName', 'CollectionPhase',
                    'SlideEvent', 'Participant', 'SampleNumber', 'Anger',
                    'Contempt', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise', 
                    'Engagement', 'Valence', 'Sentimentality', 'Confusion', 'Neutral', 'ET_GazeLeftx', 'ET_GazeLefty', 'ET_GazeRightx',
                    'ET_GazeRighty', 'ET_PupilLeft', 'ET_PupilRight' ]
        os.makedirs(output_path, exist_ok=True)
        for file in os.listdir(raw_path):
            file_path = os.path.join(raw_path, file)
            try:
                df = pd.read_csv(file_path, header=None, low_memory=False)
            except pd.errors.ParserError as e:
                messagebox.showerror("Error", f"Error reading CSV file: {file_path}\n{e}")
                continue
            filename = file.split(".")[0].split("_")[1]
            cleaned_df = file_clean(df, filename)
            if cleaned_df is not None:
                cleaned_df = cleaned_df[columns_to_keep]
                cleaned_csv_filename = f"{filename}_cleaned.csv"
                cleaned_csv_path = os.path.join(output_path, cleaned_csv_filename)
                cleaned_df.to_csv(cleaned_csv_path, index=False)

    def browse_raw_folder():
        folder_path = filedialog.askdirectory()
        raw_path_var.set(folder_path)

    def browse_output_folder():
        folder_path = filedialog.askdirectory()
        output_path_var.set(folder_path)

    def execute_cleaning():
        raw_path = raw_path_var.get()
        output_path = output_path_var.get()
        if not raw_path or not output_path:
            messagebox.showerror("Error", "Please select both input and output directories.")
            return
        clean_files(raw_path, output_path)
        messagebox.showinfo("Info", "Files cleaned successfully!")

    # Step 2 For Convert Cleaned Csv into Xlx
    def read_csv_file():
        file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        return file_path

    def save_excel(df, participant_name, base_path):
        save_path = os.path.join(base_path, f"{participant_name}.xlsx")
        
        workbook = Workbook()

        emotion_columns = ['Anger', 'Contempt', 'Disgust', 'Fear', 'Joy', 
                        'Sadness', 'Surprise', 'Engagement', 'Valence', 
                        'Sentimentality', 'Confusion', 'Neutral']

        for source_stimuli_name in df['SourceStimuliName'].unique():
            sheet = workbook.create_sheet(title=source_stimuli_name[:31])  # Excel sheet names have a maximum length of 31 characters
            
            filtered_df = df[df['SourceStimuliName'] == source_stimuli_name]
            
            # Replace empty strings and NaN with 0 in the specific columns of the filtered DataFrame
            filtered_df[emotion_columns] = filtered_df[emotion_columns].replace("", 0).fillna(0)

            # Select the desired columns
            columns = ['Timestamp', 'Row', 'StimType', 'Duration', 'SourceStimuliName',
                'CollectionPhase', 'SlideEvent', 'Participant', 'SampleNumber',
                'SampleNumber.1', 'SampleNumber.2', 'Anger', 'Contempt', 'Disgust',
                'Fear', 'Joy', 'Sadness', 'Surprise', 'Engagement', 'Valence',
                'Sentimentality', 'Confusion', 'Neutral', 'ET_GazeLeftx', 'ET_GazeLefty', 'ET_GazeRightx',
                    'ET_GazeRighty', 'ET_PupilLeft', 'ET_PupilRight' ]
            
            #filtered_df[columns] = filtered_df[columns].replace("", 0).fillna(0)
            
            sheet.append(columns)
            for row in filtered_df[columns].itertuples(index=False):
                sheet.append(row)

        workbook.remove(workbook['Sheet'])
        workbook.save(save_path)

    def main_process():
        file_path = read_csv_file()
        if file_path:
            df = pd.read_csv(file_path)
            participant_name = df['Participant'].iloc[0]  # Extracting the participant's name from the first row
            base_path = os.path.dirname(file_path)
            save_excel(df, participant_name, base_path)
            messagebox.showinfo("Success", f"Excel file has been generated and saved as {participant_name}.xlsx!")
        else:
            messagebox.showwarning("Error", "Unable to read CSV file.")

    # Step 3 Functions
    # Function to select the Excel file
    def select_excel_file():
        excel_file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if excel_file_path:
            entry_excel_file.delete(0, tk.END)
            entry_excel_file.insert(0, excel_file_path)

    # Function to select the image file
    def select_image_file():
        image_file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
        if image_file_path:
            entry_image_file.delete(0, tk.END)
            entry_image_file.insert(0, image_file_path)

    # Function to create and save individual plots for each emotion
    def create_and_save_plot():
        global plot_index, plot_queue
         
        plot_queue.clear()
        # Get the file paths and sheet name from the entry fields
        excel_file_path = entry_excel_file.get()
        sheet_name = entry_sheet_name.get()
        image_file_path = entry_image_file.get()

        if not excel_file_path or not sheet_name or not image_file_path:
            print("Please select all required files and enter the sheet name.")
            return

        # Load the data from the Excel file
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        df.dropna(subset=['ET_GazeLeftx', 'ET_GazeLefty', 'ET_GazeRightx', 'ET_GazeRighty'], inplace=True)

        # Calculate the normalized x and y coordinates
        df['norm_x'] = ((df['ET_GazeLeftx'] + df['ET_GazeRightx']) / 2) / 1920
        df['norm_y'] = ((df['ET_GazeLefty'] + df['ET_GazeRighty']) / 2) / 1080

        # Sort data by y-coordinate
        df = df.sort_values('norm_y')
        
        # Rest of the code for data processing and plotting...

        emotions = ['Anger', 'Contempt', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise', 'Engagement', 'Valence', 'Sentimentality', 'Confusion', 'Neutral']
        # Create a dictionary to store alpha values for each emotion
        
        emotion_alpha = {
                'Anger': 0.02,
                'Contempt': 0.09,
                'Disgust': 0.15,
                'Fear': 0.21,
                'Joy': 0.32,
                'Sadness': 0.4,
                'Surprise': 0.52,
                'Engagement': 0.6,
                'Valence': 0.7,
                'Sentimentality': 0.8,
                'Confusion': 0.9,
                'Neutral': 1.0
            }

            # Create a custom colormap that transitions from white to red
        cdict = {'red':   [[0.0, 1.0, 1.0], [1.0, 1.0, 1.0]],
                    'green': [[0.0, 1.0, 1.0], [1.0, 0.0, 0.0]],
                    'blue':  [[0.0, 1.0, 1.0], [1.0, 0.0, 0.0]]}
        red_to_white_cmap = LinearSegmentedColormap('RedToWhite', cdict)

            # Function to get emotion color based on value and alpha
        def get_emotion_color_alpha(value, emotion):
                alpha_val = emotion_alpha[emotion]
                color = red_to_white_cmap(value)
                return color[:3] + (alpha_val,)


        for emotion1 in emotions:
            # Create the figure and subplots for each emotion comparison
            fig, axs = plt.subplots(1, 2, figsize=(15, 6))
            figs.append(fig)

            # Left subplot - Scatter plot for the current emotion
            sc = axs[0].scatter(df['norm_x'], df['norm_y'], c=df[emotion1], cmap=red_to_white_cmap, label=f'{emotion1} Emotion Points', alpha=0.8, s=100)
            axs[0].set_title(f'{emotion1} Emotion Points')
            axs[0].set_xlabel('Normalized X-coordinate')
            axs[0].set_ylabel('Normalized Y-coordinate')

            # Set the axis ticks for the left subplot
            axs[0].set_xticks([0, 0.5, 1])
            axs[0].set_yticks([0, 0.5, 1])

            # Right subplot - Heatmap of eye gaze points with the current emotion levels
            sns.kdeplot(data=df, x='norm_x', y='norm_y', fill=True, thresh=0.05, levels=10, cmap=red_to_white_cmap, ax=axs[1], alpha=0.4)
            axs[1].set_title(f'Eye Gaze Heatmap with {emotion1} Emotion')
            axs[1].set_xlabel('Normalized X-coordinate')
            axs[1].set_ylabel('Normalized Y-coordinate')

            # Create a custom colorbar for the current emotion
            cbar_emotion = plt.colorbar(sc, ax=axs[1])
            cbar_emotion.set_label(f'{emotion1} Level')

            # Add the current emotion points as scatter points overlaid on the heatmap
            sc = axs[1].scatter(df['norm_x'], df['norm_y'], c=df[emotion1], cmap=red_to_white_cmap, label=f'{emotion1} Emotion Points', alpha=0.8, s=100)

            # Update the color and alpha values for the scatter points based on emotion values
            sc.set_array(df[emotion1])
            sc.set_cmap(red_to_white_cmap)
            sc.set_color([get_emotion_color_alpha(val, emotion1) for val in df[emotion1]])

            # Add legend on the right subplot
            axs[1].legend()

            # Load the image
            image = Image.open(image_file_path)

            # Resize the image to match the figure size
            fig_width, fig_height = fig.get_size_inches()
            resized_image = image.resize((int(fig_width * image.width), int(fig_height * image.height)))

            # Overlay the resized image with transparency (alpha) on both subplots
            axs[0].imshow(resized_image, extent=[0, 1, 0, 1], alpha=0.9, aspect='auto')
            axs[1].imshow(resized_image, extent=[0, 1, 0, 1], alpha=0.9, aspect='auto')

            plot_queue.append(fig)

            # # Create a canvas widget in the Tkinter window
            # canvas = FigureCanvasTkAgg(fig, master=root)  
            # canvas.draw()  # Draw the plot onto the canvas
            # canvas.get_tk_widget().pack()  # Add the canvas widget to the window
            participant_name = df['Participant'].iloc[0]
            output_folder = os.path.join("Output", participant_name, sheet_name)
            os.makedirs(output_folder, exist_ok=True)
            output_file_path = os.path.join(output_folder, f"{sheet_name}_{emotion1}_{plot_index}_plot.png")
            fig.savefig(output_file_path)

            plot_index += 1

        messagebox.showinfo("Info", "All plots generated and saved!")

    def show_plot():
        global plot_window, canvas

        if plot_window:  # Check and destroy the previous plot_window if it exists
            plot_window.destroy()
            plot_window = None
            canvas = None

        if experiment.get() == "New":
            for root, dirs, _ in os.walk("Output"):
                for dir_name in dirs:
                    plot_dir = os.path.join(root, dir_name)
                    show_image_from_dir(plot_dir)
        else:
            participant = participant_menu.get()
            sheet = sheet_menu.get()
            if participant and sheet:
                plot_dir = os.path.join("Output", participant, sheet)
                if os.path.exists(plot_dir):
                    show_image_from_dir(plot_dir)
                else:
                    print(f"Directory {plot_dir} does not exist.")
    
    
    def show_saved_plots(root):
        global plot_window, canvas

        if plot_window:
            plot_window.destroy()
            plot_window = None
            canvas = None

        plot_window = tk.Toplevel(root)
        plot_window.title("Saved Plots")
        plot_window.state('zoomed')

        canvas_frame = ttk.Frame(plot_window)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Vertical scrollbar
        canvas_scroll_v = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        canvas_scroll_v.pack(side=tk.RIGHT, fill=tk.Y)

        # Horizontal scrollbar
        canvas_scroll_h = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        canvas_scroll_h.pack(side=tk.BOTTOM, fill=tk.X)

        canvas = tk.Canvas(canvas_frame, yscrollcommand=canvas_scroll_v.set, xscrollcommand=canvas_scroll_h.set)
        canvas.pack(fill=tk.BOTH, expand=True)

        canvas_scroll_v.config(command=canvas.yview)
        canvas_scroll_h.config(command=canvas.xview)  # Set the horizontal scrollbar to scroll the canvas
        inner_canvas = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_canvas, anchor="nw")

        # Directory where the saved plots are located
        output_folder = "Output"

        # Retrieve a list of image files in the nested folders
        image_files = []
        for root, _, files in os.walk(output_folder):
            for filename in files:
                if filename.endswith(".png"):
                    image_files.append(os.path.join(root, filename))

        print(image_files)

        photo_images = []  # Keep references to PhotoImage objects

        # Iterate through the image files and display them
        for idx, image_file in enumerate(image_files):
            img = tk.PhotoImage(file=image_file)
            photo_images.append(img)  # Keep the reference
            img_label = tk.Label(inner_canvas, image=img)
            img_label.image = img  # Keep a reference to the PhotoImage object
            img_label.grid(row=idx, column=0, padx=10, pady=10)

        canvas.update_idletasks()  # Update the canvas size

        canvas.config(scrollregion=canvas.bbox("all"))
        canvas.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

        # Keep references to PhotoImage objects
        canvas.photo_images = photo_images

    def on_closing():
        global plot_window
        plot_window.destroy()
        plot_window = None

    def show_image_from_figure(input_data):
        global plot_window, canvas

        plt.close('all')

        if isinstance(input_data, np.ndarray):
            fig, ax = plt.subplots()
            ax.imshow(input_data)
        else:
            fig = input_data

        ax.axis('off')

        if not plot_window:  # If the plot window hasn't been created yet
            plot_window = tk.Toplevel(root)
            plot_window.protocol("WM_DELETE_WINDOW", on_closing)

            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=tk.YES, fill=tk.BOTH)

            # Create the buttons only once (assuming you've defined show_previous_plot and show_next_plot functions)
            previous_plot_button = ttk.Button(plot_window, text="Previous Plot", command=show_previous_plot)
            previous_plot_button.pack(side=tk.LEFT, padx=10, pady=10)

            next_plot_button = ttk.Button(plot_window, text="Next Plot", command=show_next_plot)
            next_plot_button.pack(side=tk.RIGHT, padx=10, pady=10)

        else:  # If the plot window already exists
            canvas.get_tk_widget().destroy()

            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=tk.YES, fill=tk.BOTH)

    def show_image_from_dir(directory):
        global pending_plots

        # Gather all the images from the directory and add to the pending queue
        for filename in sorted(os.listdir(directory)):
            if filename.endswith('.png'):
                img_path = os.path.join(directory, filename)
                pending_plots.append(img_path)

        # If there are any images in the queue, show the first one
        if pending_plots:
            next_image = pending_plots.pop(0)
            img = plt.imread(next_image)
            seen_plots.append(next_image)
            show_image_from_figure(img)

    def show_previous_plot():
        global seen_plots, pending_plots

        if len(seen_plots) > 1:  # If there is more than one image in seen_plots
            # Move the last shown image to pending_plots and remove it from seen_plots
            pending_image = seen_plots.pop()
            pending_plots.insert(0, pending_image)

            # Load and display the previous image
            prev_image_path = seen_plots[-1]
            img = plt.imread(prev_image_path)
            show_image_from_figure(img)

    def show_next_plot():
        global seen_plots, pending_plots

        if pending_plots:  # If there are images left to be shown
            next_image_path = pending_plots.pop(0)
            img = plt.imread(next_image_path)
            seen_plots.append(next_image_path)
            show_image_from_figure(img)

    def update_sheets_dropdown(*args):
        selected_participant = participant_var.get()
        if selected_participant:
            participant_dir = os.path.join(base_dir, selected_participant)
            sheets = [name for name in os.listdir(participant_dir) if os.path.isdir(os.path.join(participant_dir, name))]
            sheet_var.set('')  # reset sheet value
            sheet_menu["values"] = sheets

    def update_participants_and_sheets():
        participants = [name for name in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, name))]
        participant_var.set('')  # reset participant value
        participant_menu["values"] = participants
        sheet_var.set('')  # reset sheet value
        sheet_menu["values"] = []  # reset sheet menu

    def update_gui(*args):
        selection = experiment.get()

        if selection == "New":
            # Show widgets for "New" option
            button_select_excel.pack(pady=10)
            entry_excel_file.pack(pady=20)
            label_sheet_name.pack(pady=10)
            entry_sheet_name.pack(pady=10)
            button_select_image.pack(pady=10)
            entry_image_file.pack(pady=20)
            generate_button.pack(pady=20)
            # Hide widgets for "Existing" option
            participant_menu.pack_forget()
            sheet_menu.pack_forget()
        else:
            # Here, you would typically update the dropdowns for the "Existing" option
            # update_participants_and_sheets() 
            # Show widgets for "Existing" option
            participant_menu.pack(pady=10)
            sheet_menu.pack(pady=10)
            # Hide widgets for "New" option
            button_select_excel.pack_forget()
            entry_excel_file.pack_forget()
            label_sheet_name.pack_forget()
            entry_sheet_name.pack_forget()
            button_select_image.pack_forget()
            entry_image_file.pack_forget()
            generate_button.pack_forget()

    root.title("Multi-step GUI")
    root.geometry("500x500")
    root.state('zoomed')

    # Create the notebook (tab controller)
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    # Step 1 Tab
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Step 1 - CSV Cleaner")

    raw_path_var = tk.StringVar()
    output_path_var = tk.StringVar()

    tk.Label(tab1, text="Select raw data folder:").pack(pady=10)
    tk.Entry(tab1, textvariable=raw_path_var, width=50).pack(padx=10)
    tk.Button(tab1, text="Browse", command=browse_raw_folder).pack(pady=5)
    tk.Label(tab1, text="Select output folder:").pack(pady=10)
    tk.Entry(tab1, textvariable=output_path_var, width=50).pack(padx=10)
    tk.Button(tab1, text="Browse", command=browse_output_folder).pack(pady=5)
    tk.Button(tab1, text="Execute Cleaning", command=execute_cleaning).pack(pady=20)

    # Step 2 Tab
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Step 2 - CSV to Excel Converter")

    start_btn = tk.Button(tab2, text="Convert CSV to Excel", command=main_process)
    start_btn.pack(pady=50)

    # Step 3 Tab
    # Step 3 Tab
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text="Step 3 - Eye Gaze Plot with Emotions Overlay")
    
    

    experiment = tk.StringVar()
    participant_menu = tk.StringVar()
    sheet_menu = tk.StringVar()
    plot_queue = deque()
    seen_plots = []
    participant_var = tk.StringVar()
    sheet_var = tk.StringVar()

    # Radiobuttons for selection
    new_rb = ttk.Radiobutton(tab3, text="New Experiment", variable=experiment, value="New")
    new_rb.pack(pady=10)

    existing_rb = ttk.Radiobutton(tab3, text="Existing Experiment", variable=experiment, value="Existing")
    existing_rb.pack(pady=10)
    
    

    # Widgets for "New" option
    entry_excel_file = ttk.Entry(tab3, font=("Arial", 12))
    entry_excel_file.pack(pady=10)

    button_select_excel = ttk.Button(tab3, text="Select Excel File", command=select_excel_file)
    button_select_excel.pack(pady=5)

    label_sheet_name = ttk.Label(tab3, text="Enter sheet name:", font=("Arial", 14))
    label_sheet_name.pack(pady=10)

    entry_sheet_name = ttk.Entry(tab3, font=("Arial", 12))
    entry_sheet_name.pack(pady=10)

    entry_image_file = ttk.Entry(tab3, font=("Arial", 12))
    entry_image_file.pack(pady=10)

    button_select_image = ttk.Button(tab3, text="Select Image File", command=select_image_file)
    button_select_image.pack(pady=5)

    # Button to generate and save plots
    generate_button = ttk.Button(tab3, text="Generate and Save Plots", command=create_and_save_plot)
    generate_button.pack( pady=10)
    
    # Button to show saved plots
    show_saved_button = ttk.Button(tab3, text="Show Saved Plots", command=lambda: show_saved_plots(root))
    show_saved_button.pack(side=tk.BOTTOM,pady=(0, 180))

    
    
    # Widgets for "Existing" option
    participant_menu = ttk.Combobox(tab3)  # This should be populated with participants
    sheet_menu = ttk.Combobox(tab3)        # This should be populated with sheets based on the participant

    # Update the GUI when the selection changes
    experiment.trace("w", update_gui)
    participant_var.trace("w", update_sheets_dropdown)

    # Set the initial state
    update_gui()
    
