
import pandas as pd
import numpy as np
import cv2
import os
from skimage.metrics import structural_similarity as ssim
from IPython.display import Image, display
import shutil
import tkinter as tk
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
from PIL import Image as PILImage
from tkinter import scrolledtext


import warnings
warnings.filterwarnings('ignore')
import gc

def calculate_timestamps(video_path):
    # Open the video file
    video = cv2.VideoCapture(video_path)

    # Get the frame rate and duration of the video
    fps = video.get(cv2.CAP_PROP_FPS)
    duration = video.get(cv2.CAP_PROP_FRAME_COUNT) / fps

    # Initialize the list to store timestamps
    timestamps = []
    frames = []

    # Calculate timestamps for each frame
    for frame_num in range(int(video.get(cv2.CAP_PROP_FRAME_COUNT))):
        timestamp = frame_num / fps
        timestamps.append(timestamp)
        frames.append(frame_num)

    # Release the video capture object
    video.release()

    return timestamps, duration,frames


def get_top_three_frames_for_emotion(merged_df, emotion, base_output_dir):
    # Create directory path based on the selected emotion
    emotion_dir = os.path.join(base_output_dir, "emotions", emotion)
    if not os.path.exists(emotion_dir):
        os.makedirs(emotion_dir)

    emotion_df = merged_df[merged_df['Variable'] == emotion]
    top_three_emotion_df = emotion_df.nlargest(3, 'Max_Values')

    # Displaying the frames for top three emotions and saving them in the designated directory
    for index, row in top_three_emotion_df.iterrows():
        print(f"Frame: {row['Frames']}, Variable: {row['Variable']}, Max Value: {row['Max_Values']}")
        
        # Define the new save path for the image
        new_image_path = os.path.join(emotion_dir, os.path.basename(row['Path']))
        
        # Copy the image to the new location
        shutil.copy(row['Path'], new_image_path)
        
        # Update the path in the DataFrame to reflect the new location
        row['Path'] = new_image_path
        
        # Display the image
        # display(Image(filename=new_image_path))  

        # Use these lines:
        image = PILImage.open(new_image_path)
        # image.show()

    return top_three_emotion_df


def main_code(video_path, csv_path,experiment_name,user_name,selected_emotion):
    data = pd.read_csv(csv_path,low_memory=(False))
    data.columns = list(data.iloc[31])
    data = data[32:].reset_index(drop=True)
    
    print(data.head(5))
    # Emotion Data
    emotion_data = data[['Row','Timestamp','SourceStimuliName','Anger','Contempt',
                         'Disgust','Fear','Joy','Sadness','Surprise','Engagement',
                         'Valence','Sentimentality','Confusion','Neutral','Attention']]
    emotions = emotion_data.drop(['Timestamp','SourceStimuliName','Row'],axis=1).columns

    print(data.columns)


    # GSR Data
    gsr_data = data[['Row','Timestamp','SourceStimuliName','Phasic Signal']]
    gsr = gsr_data.drop(['Timestamp','SourceStimuliName','Row'],axis=1).columns

    # Heart Rate Data
    hr_data = data[['Row','Timestamp','SourceStimuliName','Heart Rate PPG ALG']]
    hr = hr_data.drop(['Timestamp','SourceStimuliName','Row'],axis=1).columns
    
    emotion_data[emotions] = emotion_data[emotions].astype('float64')
    emotion_data = emotion_data.dropna(subset=emotions)
    emotion_data["Timestamp"] = emotion_data["Timestamp"].astype('float64')
    emotion_data["Row"] = emotion_data["Row"].astype('int64')
    emotion_data["SourceStimuliName"] = emotion_data["SourceStimuliName"].astype('int64').astype('float64')
    emotion_data = emotion_data.loc[emotion_data.SourceStimuliName==1].reset_index(drop=True)

    min_emotion_timestamp = emotion_data["Timestamp"].min()

    # Convert 'imotion_data' timestamp to datetime if not already
    emotion_data['Timestamp'] = pd.to_datetime(emotion_data['Timestamp'])
    emotion_data.index = emotion_data["Timestamp"]
    emotion_data = emotion_data.drop("Timestamp",axis=1)

    # Resample data to the bin size
    emotion_data = emotion_data.resample('0.00015ms').mean()
    print(emotion_data.head(5))
    
    gsr_data[gsr] = gsr_data[gsr].astype('float64')
    gsr_data = gsr_data.dropna(subset=gsr)
    gsr_data["Timestamp"] = gsr_data["Timestamp"].astype('float64')
    gsr_data["Row"] = gsr_data["Row"].astype('int64')
    gsr_data["SourceStimuliName"] = gsr_data["SourceStimuliName"].astype('int64').astype('float64')
    gsr_data = gsr_data.loc[gsr_data.SourceStimuliName==1].reset_index(drop=True)

    min_gsr_timestamp = gsr_data["Timestamp"].min()

    # Convert 'imotion_data' timestamp to datetime if not already
    gsr_data['Timestamp'] = pd.to_datetime(gsr_data['Timestamp'])
    gsr_data.index = gsr_data["Timestamp"]
    gsr_data = gsr_data.drop("Timestamp",axis=1)

    # Resample data to the bin size
    gsr_data = gsr_data.resample('0.00015ms').mean()
    print(gsr_data.head(5))
    
    hr_data[hr] = hr_data[hr].astype('float64')
    hr_data = hr_data.dropna(subset=hr)
    hr_data["Timestamp"] = hr_data["Timestamp"].astype('float64')
    hr_data["Row"] = hr_data["Row"].astype('int64')
    hr_data["SourceStimuliName"] = hr_data["SourceStimuliName"].astype('int64').astype('float64')
    hr_data = hr_data.loc[hr_data.SourceStimuliName==1].reset_index(drop=True)

    min_hr_timestamp = hr_data["Timestamp"].min()

    # Convert 'imotion_data' timestamp to datetime if not already
    hr_data['Timestamp'] = pd.to_datetime(hr_data['Timestamp'])
    hr_data.index = hr_data["Timestamp"]
    hr_data = hr_data.drop("Timestamp",axis=1)

    # Resample data to the bin size
    hr_data = hr_data.resample('0.00015ms').mean()
    print(hr_data.head(5))
    
    
    video_path = video_path
    timestamps,duration,frames = calculate_timestamps(video_path)

    # merge the frame with the emotion data
    # Emotion 
    t_df_emotion = pd.DataFrame(data={"Frames":frames,"Timestamp":[(i*1000)+min_emotion_timestamp for i in timestamps]})
    t_df_emotion['Timestamp'] = pd.to_datetime(t_df_emotion['Timestamp'])
    t_df_emotion.index = t_df_emotion["Timestamp"]
    t_df_emotion = t_df_emotion.drop("Timestamp",axis=1)
    t_df_emotion = t_df_emotion.resample('0.00015ms').mean()

    # Merge frames with gsr data
    # GSR
    t_df_gsr = pd.DataFrame(data={"Frames":frames,"Timestamp":[(i*1000)+min_gsr_timestamp for i in timestamps]})
    t_df_gsr['Timestamp'] = pd.to_datetime(t_df_gsr['Timestamp'])
    t_df_gsr.index = t_df_gsr["Timestamp"]
    t_df_gsr = t_df_gsr.drop("Timestamp",axis=1)
    t_df_gsr = t_df_gsr.resample('0.00015ms').mean()

    # Merge frame with heart rate data
    # Heart Rate 
    t_df_hr = pd.DataFrame(data={"Frames":frames,"Timestamp":[(i*1000)+min_hr_timestamp for i in timestamps]})
    t_df_hr['Timestamp'] = pd.to_datetime(t_df_hr['Timestamp'])
    t_df_hr.index = t_df_hr["Timestamp"]
    t_df_hr = t_df_hr.drop("Timestamp",axis=1)
    t_df_hr = t_df_hr.resample('0.00015ms').mean()

    merged_emotion_data = pd.merge_asof(emotion_data,t_df_emotion, left_index=True, right_index=True)
    merged_gsr_data = pd.merge_asof(gsr_data,t_df_gsr, left_index=True, right_index=True)
    merged_hr_data = pd.merge_asof(hr_data,t_df_hr, left_index=True, right_index=True)
    
    # Top 3 Peaks for each Emotion
    merged_emotion_data = merged_emotion_data.reset_index()
    top_three_emotion = pd.DataFrame()
    for emot in emotions:
        temp = merged_emotion_data[['Timestamp','SourceStimuliName','Frames']+[emot]]
        temp[emot] = temp[emot].astype('float64')
        temp = temp.sort_values(by=[emot],ascending=False)
        temp = temp.iloc[:3].reset_index(drop=True)
        temp = pd.melt(temp,id_vars=['Timestamp','SourceStimuliName','Frames'],var_name="Variable",value_name="Max_Values")
        temp["Frames"] = temp["Frames"].round()
        top_three_emotion = pd.concat([top_three_emotion,temp],axis=0)
    print(top_three_emotion.head(5))
    
    merged_gsr_data = merged_gsr_data.reset_index()
    top_three_gsr = pd.DataFrame()
    for emot in gsr:
        temp = merged_gsr_data[['Timestamp','SourceStimuliName','Frames']+[emot]]
        temp[emot] = temp[emot].astype('float64')
        temp = temp.sort_values(by=[emot],ascending=False)
        temp = temp.iloc[:3].reset_index(drop=True)
        temp = pd.melt(temp,id_vars=['Timestamp','SourceStimuliName','Frames'],var_name="Variable",value_name="Max_Values")
        temp["Frames"] = temp["Frames"].round()
        top_three_gsr = pd.concat([top_three_gsr,temp],axis=0)
    print(top_three_gsr.head(5))
    
    merged_hr_data = merged_hr_data.reset_index()
    top_three_hr = pd.DataFrame()
    for emot in hr:
        temp = merged_hr_data[['Timestamp','SourceStimuliName','Frames']+[emot]]
        temp[emot] = temp[emot].astype('float64')
        temp = temp.sort_values(by=[emot],ascending=False)
        temp = temp.iloc[:3].reset_index(drop=True)
        temp = pd.melt(temp,id_vars=['Timestamp','SourceStimuliName','Frames'],var_name="Variable",value_name="Max_Values")
        temp["Frames"] = temp["Frames"].round()
        top_three_hr = pd.concat([top_three_hr,temp],axis=0)
    print(top_three_hr.head(5))
    
    top_three = pd.concat([top_three_emotion,top_three_gsr,top_three_hr]).reset_index(drop=True)
    print(top_three.head(5))
    
    # Set output directory
    experiment_dir = os.path.join("experiments", experiment_name)
    user_dir = os.path.join(experiment_dir, user_name)
    output_dir = os.path.join(user_dir, "output")


    # Create output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the video file
    video = cv2.VideoCapture(video_path)

    # Initialize frame counter
    count = 0

    # Initialize variable to hold the previous frame
    prev_frame = None

    # Initialize DataFrame to hold output data
    df_output = pd.DataFrame(columns=["Frame_Name", "Timestamp", "Path"])

    # Check if video opened successfully
    if not video.isOpened():
        print("Error opening video file")

    while video.isOpened():
        # Read a frame
        ret, frame = video.read()

        if ret:
            # Convert the frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Add Gaussian blur to gray_frame
            gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            # If this is the first frame, just save it to prev_frame
            if prev_frame is None:
                prev_frame = gray_frame
            else:
                # Compare the current frame with the previous frame
                similarity = ssim(prev_frame, gray_frame)

                # If similarity is below a certain threshold, assume a scroll has occurred
                if similarity < 0.9:  # Adjusted the threshold
                    # Get the timestamp of the current frame (in milliseconds)
                    timestamp = video.get(cv2.CAP_PROP_POS_MSEC)

                    # Save the frame
                    frame_name = f"frame_{count}.png"
                    frame_path = os.path.join(output_dir, frame_name)
                    cv2.imwrite(frame_path, frame)

                    # Append data to the DataFrame
                    # df_output = df_output.append({"Frame_Name": frame_name, "Timestamp": timestamp, "Path": frame_path},
                    #                              ignore_index=True)
                    new_row = pd.DataFrame([{"Frame_Name": frame_name, "Timestamp": timestamp, "Path": frame_path}])
                    df_output = pd.concat([df_output, new_row], ignore_index=True)
                # Update prev_frame
                prev_frame = gray_frame

            count += 1

        else:
            # If no frame is read, then we have reached the end of the video
            break

    # Release the video file
    video.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()

    # Print DataFrame
    # print(df_output)
    
    emotion_df = top_three.copy()
    output_df = df_output.copy()
    
    output_df['Frame_Name'] = output_df['Frame_Name'].apply(lambda x: int(x.split('_')[1].split('.')[0]))
    
    # Create a new DataFrame to store the merged data
    merged_df = pd.DataFrame()

    # Iterate over the rows in the emotion data
    for idx, row in emotion_df.iterrows():
        # Find the frame with the closest Frames value to the current row's Frames value
        closest_frame = output_df.iloc[(output_df['Frame_Name'] - row['Frames']).abs().argsort()[:1]]

        # Duplicate the current row and add the Path from the closest frame
        new_row = row.copy()
        new_row['Path'] = closest_frame['Path'].values[0]

        # Append the new row to the merged DataFrame
        # merged_df = merged_df.append(new_row, ignore_index=True)
        new_df = pd.DataFrame([new_row])
        merged_df = pd.concat([merged_df, new_df], ignore_index=True)
        
    # # Call this function with the emotion name to get the top three frames
    # output_dir = os.path.join("output", "emotions", selected_emotion)
    # top_three_frames = get_top_three_frames_for_emotion(merged_df, selected_emotion)

    base_output_dir = os.path.join("experiments", experiment_name, user_name)
    top_three_frames = get_top_three_frames_for_emotion(merged_df, selected_emotion, base_output_dir)

    return merged_df, top_three_frames


    



# Function to be executed with the provided paths
def process_video_and_csv(video_path, csv_path, experiment_name, user_name, selected_emotion):
    # Your processing logic here
    print("Processing video:", video_path)
    print("Processing CSV:", csv_path)

    # Create directories based on the experiment name and user name
    output_dir = os.path.join("experiments", experiment_name, user_name)
    os.makedirs(output_dir, exist_ok=True)

    # Copy video and CSV to the appropriate directories (optional)
    shutil.copy(video_path, os.path.join(output_dir, os.path.basename(video_path)))
    shutil.copy(csv_path, os.path.join(output_dir, os.path.basename(csv_path)))


    top_three_frames = main_code(video_path, csv_path,experiment_name,user_name,selected_emotion)
    return top_three_frames


# Tkinter app
class VideoProcessingApp:
    
    def __init__(self, root):

        self.root = root
        self.root.title("Video Processing App")
        self.images_frame = None

        self.image_labels = []

        self.exp_frame = ttk.LabelFrame(root, text="Experiment Details")
        self.exp_frame.pack(padx=20, pady=10, fill="both", expand="yes")

        self.exp_name_label = ttk.Label(self.exp_frame, text="Experiment Name:")
        self.exp_name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.exp_name_entry = ttk.Entry(self.exp_frame)
        self.exp_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")

        self.user_name_label = ttk.Label(self.exp_frame, text="User Name:")
        self.user_name_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.user_name_entry = ttk.Entry(self.exp_frame)
        self.user_name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="we")
        
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50")

        self.video_frame = ttk.LabelFrame(root, text="Video Input")
        self.video_frame.pack(padx=20, pady=10, fill="both", expand="yes")

        self.video_path_label = ttk.Label(self.video_frame, text="Video Path:")
        self.video_path_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.video_path_entry = ttk.Entry(self.video_frame)
        self.video_path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")

        self.video_browse_button = ttk.Button(self.video_frame, text="Browse", command=self.browse_video_path)
        self.video_browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.csv_frame = ttk.LabelFrame(root, text="CSV Input")
        self.csv_frame.pack(padx=20, pady=10, fill="both", expand="yes")

        self.csv_path_label = ttk.Label(self.csv_frame, text="CSV Path:")
        self.csv_path_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.csv_path_entry = ttk.Entry(self.csv_frame)
        self.csv_path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")

        self.csv_browse_button = ttk.Button(self.csv_frame, text="Browse", command=self.browse_csv_path)
        self.csv_browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.run_button = ttk.Button(root, text="Run", command=self.run_processing, style="TButton")
        self.run_button.pack(padx=20, pady=10)

        list_of_emotions = ['Anger', 'Joy', 'Sadness', 'Fear', 'Surprise', 'Disgust', 'Neutral', 'Contempt', 'Engagement', 'Valence','Phasic Signal','Heart Rate PPG ALG']

        self.result_button = ttk.Button(root, text="Show Results", command=self.display_selected_emotion, style="TButton")
        self.result_button.pack(padx=20, pady=10)


        self.emotion_label = ttk.Label(self.exp_frame, text="Select Emotion:")
        self.emotion_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.emotion_var = tk.StringVar(self.root)
        self.emotion_dropdown = ttk.Combobox(self.exp_frame, textvariable=self.emotion_var, values=list_of_emotions)
        self.emotion_dropdown.bind("<<ComboboxSelected>>", self.display_selected_emotion)

        self.emotion_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="we")
        # Create a scrollable frame for displaying images and values
        self.scrollable_frame = ttk.LabelFrame(root, text="Emotion Images and Values")
        self.scrollable_frame.pack(padx=20, pady=20, fill="both", expand="yes")

        self.canvas = tk.Canvas(self.scrollable_frame)
        self.scrollbar_y = ttk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self.scrollable_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        
        


    def browse_video_path(self):
        video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])
        self.video_path_entry.delete(0, tk.END)
        self.video_path_entry.insert(0, video_path)

    def browse_csv_path(self):
        csv_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        self.csv_path_entry.delete(0, tk.END)
        self.csv_path_entry.insert(0, csv_path)

    def run_processing(self):
        video_path = self.video_path_entry.get()
        csv_path = self.csv_path_entry.get()
        experiment_name = self.exp_name_entry.get()
        user_name = self.user_name_entry.get()
        selected_emotion = self.emotion_var.get()
        output_dir = os.path.join("experiments", experiment_name, user_name)
        os.makedirs(output_dir, exist_ok=True)

        
        # process_video_and_csv(video_path, csv_path, experiment_name, user_name, selected_emotion)
        # top_three_frames = process_video_and_csv(video_path, csv_path, experiment_name, user_name, selected_emotion)
        # top_three_frames = process_video_and_csv(video_path, csv_path, experiment_name, user_name, selected_emotion)
        self.merged_df, top_three_frames = process_video_and_csv(video_path, csv_path, experiment_name, user_name, selected_emotion)

        if top_three_frames is not None:
            image_paths = top_three_frames['Path'].tolist()
            values = top_three_frames['Max_Values'].tolist()
            self.display_emotion_images(image_paths, values)



    # def display_emotion_images(self, image_paths, values):
    
    def display_emotion_images(self, image_paths, values):
        # Remove the previous images from the inner frame
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        images_per_row = 3
        for row in range(0, len(image_paths), images_per_row):
            row_frame = ttk.Frame(self.inner_frame)
            row_frame.pack(fill="x")

            for index in range(row, min(row + images_per_row, len(image_paths))):
                image_path = image_paths[index]
                value = values[index]

                # Load and resize the image using PIL
                pil_image = PILImage.open(image_path)
                pil_image = pil_image.resize((300, 300))  # Adjust the size as necessary
                image = ImageTk.PhotoImage(pil_image)

                # Display the image
                image_label = tk.Label(row_frame, image=image)
                image_label.image = image  # keep a reference to prevent garbage collection
                image_label.pack(side="left", padx=10, pady=10)

                # Display the value below the image
                value_label = ttk.Label(row_frame, text=f"Value: {value}")
                value_label.pack(side="left", padx=10, pady=5)

        # Update the canvas and scrollbars to reflect changes in the inner frame's size
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def display_selected_emotion(self):
        selected_emotion = self.emotion_var.get()
        if hasattr(self, 'merged_df') and self.merged_df is not None:
            base_output_dir = os.path.join("experiments", self.exp_name_entry.get(), self.user_name_entry.get())
            top_three_frames = get_top_three_frames_for_emotion(self.merged_df, selected_emotion, base_output_dir)
            if top_three_frames is not None:
                image_paths = top_three_frames['Path'].tolist()
                values = top_three_frames['Max_Values'].tolist()
                
                # Clear previously displayed images and values
                for widget in self.root.winfo_children():
                    if isinstance(widget, (tk.Label, ttk.Label)) and widget not in [self.exp_frame, self.video_frame, self.csv_frame, self.run_button, self.result_button]:
                        widget.destroy()

                # Display the new images and values
                self.display_emotion_images(image_paths, values)