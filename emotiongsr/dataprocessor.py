"""
dataprocessor.py

This module contains the class DataProcessor, inspired by Mohammad,
Priyank and Sayidah's thesis. We present an OOP solution with well
documented methods and tested compatibility with iMotions 10, the
most recent version of iMotions.

Created on March 7th 2024

Colchester, Essex.

"""

import os
import warnings

import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

warnings.filterwarnings("ignore")

BASE_COLUMNS = [
    "Timestamp",
    "SourceStimuliName",
    "Participant",
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
    "ET_GazeLeftx",
    "ET_GazeLefty",
    "ET_GazeRightx",
    "ET_GazeRighty",
    "GSR RAW",
    "GSR Resistance CAL",
    "GSR Conductance CAL",
    "Heart Rate PPG ALG",
    "GSR Raw",
    "GSR Interpolated",
    "Tonic Signal",
    "Phasic Signal",
]

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

RECORDING_TIME_ROW = 8


class DataProcessor:
    """
    This class process iMotions data and generates several plots,
    its advantage against using off-the-shelf plots such as
    the ones included with iMotions is the possibility of
    working from a non-restrictive location, in other words
    no need of iMotions software other than generating the data,
    further analysis can be made in pure Python.
    """

    def __init__(self, imotions_path, output_path=None) -> None:
        self.imotions_path = imotions_path
        self.output_path = output_path
        self.data_is_clean = False

    def __load_raw_data(self):
        all_files = os.listdir(self.imotions_path)

        # Filter only CSV files
        csv_files = [f for f in all_files if f.endswith(".csv")]

        # Initialize an empty dictionary to store DataFrames
        dataframes = {}

        # Loop through all the CSV files and read them into a DataFrame
        for csv_file in csv_files:
            file_path = os.path.join(self.imotions_path, csv_file)
            dataframes[csv_file] = pd.read_csv(file_path)
        return dataframes

    def __load_clean_data(self):
        all_files = os.listdir(self.output_path)

        # Filter only CSV files
        csv_files = [f for f in all_files if f.endswith(".csv")]

        # Initialize an empty dictionary to store DataFrames
        dataframes = {}

        # Loop through all the CSV files and read them into a DataFrame
        for csv_file in csv_files:
            file_path = os.path.join(self.output_path, csv_file)
            dataframes[csv_file] = pd.read_csv(file_path)
        return dataframes

    def get_clean_data(self) -> pd.DataFrame:
        """
        This method loads the cleaned data from the folder, then
        concats all of them into a single dataframe with the timestamp
        as index
        ---
        Args
        ---
            None
        ---
        Returns
        ---
            data(pd.DataFrame) a dataframe containg clean data
            for processing
        ---
        Raises
        ---
            ValueError: if you havent called the method clean_files first
        """

        raw_dataframes = self.__load_raw_data()
        # get the first df
        start_times = []
        for _, df in raw_dataframes.items():
            time = df.iloc[RECORDING_TIME_ROW][2]  # get the start time
            time = time.split(" ")[1]
            time = time.split("+")[0]
            start_times.append(pd.to_datetime(time))
        start_times.sort()
        if not self.data_is_clean:
            raise ValueError("Clean the data first")
        dataframes = self.__load_clean_data()
        i = 0
        for _, df in dataframes.items():
            # use the first start time in the first iteration
            start_time = start_times[i]
            df["Timestamp"] = start_time + (df["Timestamp"] * pd.to_timedelta(1, unit="ms"))
            df.set_index("Timestamp", inplace=True)
            i += 1
        data = pd.DataFrame()
        for _, df in dataframes.items():
            data = pd.concat([data, df], axis=0)
        # resample data for 0.5 second intervals, use the mean for numerical columns, and the first for categorical
        # backwards fill the categorical columns
        data["SourceStimuliName"] = data["SourceStimuliName"].ffill()
        data = data.groupby(["SourceStimuliName", "Participant"]).resample("0.01s").mean()
        # the inverse of groupby, reset_index
        data = data.reset_index()
        data = data.set_index("Timestamp")

        if "ET_GazeLeftx" in data.columns:
            # Calculate the normalized x and y coordinates
            data["norm_x"] = (
                np.nan_to_num(((data["ET_GazeLeftx"] + data["ET_GazeRightx"]) / 2)) / 1920
            )
            data["norm_y"] = (
                np.nan_to_num(((data["ET_GazeLefty"] + data["ET_GazeRighty"]) / 2)) / 1080
            )
        else:
            data["norm_x"] = np.random.rand(len(data))
            data["norm_y"] = np.random.rand(len(data))
        return data

    def __clean_single_file(self, df, filename):
        df = df[df[df[0] == "Row"].index[0] :]
        df = df.reset_index(drop=True)
        df.columns = df.iloc[0].tolist()
        df = df[1:]
        df["SlideEvent"] = df["SlideEvent"].ffill()
        df = df.loc[df.SlideEvent == "StartMedia"]
        # Drop columns if they exist in the DataFrame
        columns_to_drop = ["EventSource"]
        df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)
        df = df.reset_index(drop=True)
        df["Participant"] = filename
        return df

    def clean_files(self, columns_to_keep: list = None) -> None:
        """
        This method will read all the csvs from iMotions and
        concatenate them, since there are many columns you can
        choose which columns to include.
        ---
        Args
        ---
        columns_to_keep(list) A list containing the values you want
        to use for analysis

        ---
        Returns
        ---
        None
        """
        if columns_to_keep is None:
            columns_to_keep = BASE_COLUMNS

        os.makedirs(self.output_path, exist_ok=True)
        for file in os.listdir(self.imotions_path):
            file_path = os.path.join(self.imotions_path, file)
            if not file_path.endswith(".csv"):
                continue
            try:
                df = pd.read_csv(file_path, header=None, low_memory=False)
            except pd.errors.ParserError as e:
                print("Error", f"Error reading CSV file: {file_path}\n{e}")
                continue

            filename = file.split(".")[0].split("_")[1]
            cleaned_df = self.__clean_single_file(df, filename)

            if cleaned_df is not None:
                # Keep only the columns that exist in the DataFrame
                existing_columns = [col for col in columns_to_keep if col in cleaned_df.columns]

                # If any columns are missing, print a message or log it
                missing_columns = [col for col in columns_to_keep if col not in cleaned_df.columns]
                if missing_columns:
                    print(f"Warning: Missing columns {missing_columns} in file {file}")

                cleaned_df = cleaned_df[existing_columns]
                cleaned_csv_filename = f"{filename}_cleaned.csv"
                cleaned_csv_path = os.path.join(self.output_path, cleaned_csv_filename)
                cleaned_df.to_csv(cleaned_csv_path, index=False)
        self.data_is_clean = True

    def generate_heatmap(self, data, value, image_subpath):
        # Work on a copy of the dataframe
        df = data.copy()
        # use the image path to get the stimuli name
        image_name = image_subpath.split("/")[-1].replace(".jpg", "")
        df = df[df["SourceStimuliName"] == image_name]
        # Load the image
        image_path = image_subpath
        img = cv2.imread(image_path)
        # Create a mask image to draw the emotions on
        emotion_mask = np.zeros_like(img)

        for _, row in df.iterrows():
            # Normalize coordinates to match the image dimensions
            x = int(row["norm_x"] * img.shape[1])
            y = int(row["norm_y"] * img.shape[0])

            # Plot each emotion on the mask image
            emotion_intensity = row[value]
            if emotion_intensity is not None:
                emotion_intensity = np.nan_to_num(emotion_intensity)
                # Use the intensity to set the color (or you can use it to set the size of the circle)
                intensity = int(
                    emotion_intensity * 255
                )  # Assuming the intensity is normalized between 0 and 1
                color = (intensity, intensity, intensity)  # Grayscale intensity

                # Draw a circle on the mask image
                cv2.circle(emotion_mask, (x, y), 10, color, -1)

        # Apply Gaussian blur to the emotion mask
        blurred_emotion_mask = cv2.GaussianBlur(emotion_mask, (13, 13), 11)

        heatmap_img = cv2.applyColorMap(blurred_emotion_mask, cv2.COLORMAP_JET)

        # Combine the original image with the blurred emotion mask
        result_img = cv2.addWeighted(heatmap_img, 0.5, img, 0.5, 0)

        return result_img

    def __melt_emotions(self, data, value):
        df = data.copy()

        # change emotion columns to emotion rows in the dataframe keep index and timestamp columns too
        df_emotions = df[EMOTIONS].copy()

        df_emotions["Timestamp"] = df["Timestamp"]
        df_emotions["index"] = df["index"]

        df_emotions = df_emotions.melt(
            id_vars=["Timestamp", "index"],
            value_vars=EMOTIONS,
            var_name="Emotion",
            value_name="Intensity",
        )

        df_emotions.dropna(inplace=True)
        # merge df_emotions with df on index
        df = df_emotions.merge(df, on="index")

        # Get intensity using GSR
        df["intensity"] = df[value] * df["Intensity"]

        return df

    def generate_emotion_heatmap(self, data, emotion, value, image_subpath):
        df = data.copy()

        # use the image path to get the stimuli name
        image_name = image_subpath.split("/")[-1].replace(".jpg", "")
        df = df[df["SourceStimuliName"] == image_name]

        # make an index column
        df = df.reset_index()
        df["index"] = df.index

        # melt emotions
        df = self.__melt_emotions(df, value)

        # Load the image
        image_path = image_subpath

        img = Image.open(image_path)

        df["norm_x"] = df["norm_x"] * img.size[0]
        df["norm_y"] = df["norm_y"] * img.size[1]

        color_scale = [
            [0.0, "rgba(0, 0, 255, 0)"],  # Transparent blue at the lowest value
            [0.2, "rgba(0, 0, 255, 0.2)"],  # Slightly opaque blue
            [0.4, "rgba(0, 255, 255, 0.4)"],  # Cyan
            [0.6, "rgba(0, 255, 0, 0.6)"],  # Green
            [0.8, "rgba(255, 255, 0, 0.8)"],  # Yellow
            [1.0, "rgba(255, 0, 0, 1)"],  # Fully opaque red at the highest value
        ]
        zmid = None
        if value == "Phasic Signal":
            color_scale = [
                [
                    0.0,
                    "rgba(0, 0, 255, 1)",
                ],  # Blue at the largest negative value (mapped to 0)
                [
                    0.49,
                    "rgba(0, 255, 0, 0.1)",
                ],  # Transition to transparent - slightly blue
                [0.5, "rgba(255, 255, 255, 0)"],  # Transparent at 0
                [
                    0.51,
                    "rgba(255, 255, 0, 0.1)",
                ],  # Transition from transparent - slightly red
                [1.0, "rgba(255, 0, 0, 1)"],  # Red at the largest positive value
            ]
            zmid = 0

        fig = px.imshow(img)
        fig.add_trace(
            go.Histogram2dContour(
                name=value,
                x=df[df["Emotion"] == emotion]["norm_x"],
                y=df[df["Emotion"] == emotion]["norm_y"],
                z=df[df["Emotion"] == emotion]["intensity"],
                histfunc="sum",
                colorscale=color_scale,
                zmid=zmid,
                ncontours=100,
                line=dict(width=0),
                opacity=0.9,
                contours=dict(coloring="heatmap", size=10),
                # fill the contour in all the histogram
                xaxis="x",
                yaxis="y",
                colorbar=dict(
                    title=value,
                    x=1,  # Adjust this to move the color bar closer to or further from the plot
                ),
            )
        )
        fig.update_layout(
            title=emotion,
            autosize=False,
            width=600,
            height=500,
            margin=dict(
                l=50,
                r=50,
                b=10,
                t=60,
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                visible=False,  # the axis is not visible
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                visible=False,  # the axis is visible if needed
                # domain=[0, 1],  # use the full height of the canvas
            ),
        )

        fig.update_xaxes(range=[0, img.size[0]])
        fig.update_yaxes(range=[img.size[1], 0])

        # fig.show()
        return fig

    def get_all_emotion_heatmaps(self, data, value, image_subpath):
        emotion_fig = []
        for emotion in EMOTIONS:
            fig = self.generate_emotion_heatmap(data, emotion, value, image_subpath)
            emotion_fig.append(fig)

        return emotion_fig
