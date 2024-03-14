"""
dataprocessor.py

This module contains the DataProcessor class, which is used to 
process and analyze data from iMotions and web browsing activities.

February 2024

"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from scipy.ndimage import gaussian_filter


class DataProcessor:
    """
    DataProcessor is a class that is used to
    process and analyze data from iMotions and web browsing activities.
    """

    def __init__(self, web_data_path, imotion_data_path, output_dir):
        """
        ---
        Args:
        ---
        web_data_path (str): The path to the CSV file containing the web browsing data.
        imotion_data_path (str): The path to the CSV file containing the iMotions data.
        output_dir (str): The directory where the output data and visualizations will be saved.
        """
        self.web_data_path = web_data_path
        self.imotion_data_path = imotion_data_path
        self.output_dir = output_dir
        self.output_data = pd.DataFrame(columns=["URL", "Image_Path"])
        self.web_data = pd.read_csv(
            self.web_data_path,
            skiprows=1,
            names=[
                "Time (UTC)",
                "Event",
                "Scroll Position",
                "Scroll Percentage",
                "Mouse X",
                "Mouse Y",
                "URL",
            ],
        )
        # Get the unique URLs from the data
        self.unique_urls = self.web_data["URL"].unique()

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.screenshot_paths = []
        self.mouse_activity_files = []

    def process_imotion_data(self, initial_rows_to_skip=28):
        imotion_data = pd.read_csv(
            self.imotion_data_path, skiprows=initial_rows_to_skip
        )
        # Process the data as needed
        gaze_data = imotion_data[1:-2]
        gaze_data = gaze_data.loc[~(gaze_data["ET_GazeRightx"] == -1)].reset_index(
            drop=True
        )
        gaze_data = gaze_data[
            [
                "Timestamp",
                "Anger",
                "Fear",
                "Joy",
                "Sadness",
                "Surprise",
                "Engagement",
                "Confusion",
                "Neutral",
                "ET_GazeRightx",
                "ET_GazeLeftx",
                "ET_GazeLefty",
                "ET_GazeRighty",
            ]
        ]
        # Convert the "Timestamp" column to datetime format with milliseconds
        gaze_data["Timestamp"] = pd.to_datetime(
            gaze_data["Timestamp"], unit="ms", utc=True
        )

        # Convert the datetime format to string with milliseconds
        gaze_data["Timestamp"] = gaze_data["Timestamp"].dt.strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )
        self.eye_tracking_data = gaze_data.copy()

    def process_web_data(self):
        # Replace NaN with 0 only at the beginning of each url sequence
        self.web_data.reset_index(drop=True, inplace=True)
        self.web_data["Scroll Percentage"] = (
            self.web_data.groupby(
                (self.web_data["URL"] != self.web_data["URL"].shift()).cumsum()
            )["Scroll Percentage"]
            .apply(lambda group: group.fillna(0, limit=1))
            .reset_index(drop=True)
        )

        # Fill other NaN values (not at the start of a sequence) with the last valid observation forward to next valid
        self.web_data["Scroll Percentage"].fillna(method="ffill", inplace=True)

        # fill the null for the web data
        self.web_data["Scroll Position"].fillna(method="ffill", inplace=True)
        self.web_data["Scroll Position"].fillna(method="bfill", inplace=True)
        self.web_data["Mouse X"].fillna(method="ffill", inplace=True)
        self.web_data["Mouse X"].fillna(method="bfill", inplace=True)
        self.web_data["Mouse Y"].fillna(method="ffill", inplace=True)
        self.web_data["Mouse Y"].fillna(method="bfill", inplace=True)

    def merge_web_and_imotion_data(self):

        # Make sure the timestamps are in datetime format
        self.web_data["Time (UTC)"] = pd.to_datetime(self.web_data["Time (UTC)"])
        self.eye_tracking_data["Timestamp"] = pd.to_datetime(
            self.eye_tracking_data["Timestamp"]
        )

        # Calculate the time difference for the 'eye_tracking_data' from its start
        self.eye_tracking_data["Time From Start"] = (
            self.eye_tracking_data["Timestamp"]
            - self.eye_tracking_data["Timestamp"].iloc[0]
        )

        # Apply this difference to the 'web_data' timestamps
        self.eye_tracking_data["Aligned Timestamp"] = (
            self.web_data["Time (UTC)"].iloc[0]
            + self.eye_tracking_data["Time From Start"]
        )
        # If you don't need the original timestamps or the 'Time From Start' in your final dataframe, you can drop them
        self.eye_tracking_data.drop(
            ["Timestamp", "Time From Start"], axis=1, inplace=True
        )

        # Make the 'Aligned Timestamp' the index of 'eye_tracking_data'
        self.eye_tracking_data.set_index("Aligned Timestamp", inplace=True)

        # Make 'Time (UTC)' the index of 'web_data'
        self.web_data.set_index("Time (UTC)", inplace=True)

        # Get the last not NaT time
        last_time = self.web_data.index[-2]
        size = self.web_data.index.size - 1
        self.web_data.reset_index(inplace=True)
        self.web_data.at[size, "Time (UTC)"] = last_time
        self.web_data.set_index("Time (UTC)", inplace=True)
        # Now merge both dataframes on nearest matching time
        self.merged_data = pd.merge_asof(
            self.web_data,
            self.eye_tracking_data,
            left_index=True,
            right_index=True,
            direction="nearest",
        )

        self.merged_data.reset_index(inplace=True)

    def process_data(self):
        
        self.process_imotion_data()
        self.process_merged_data()

    def process_merged_data(self):
        self.merge_web_and_imotion_data()
        # **************************** Merged Data pre-processing ********************************************************

        tmp_df = self.merged_data.copy()

        et_gaze_rightx = tmp_df["ET_GazeRightx"].interpolate(method="linear")
        et_gaze_leftx = tmp_df["ET_GazeLeftx"].interpolate(method="linear")
        et_gaze_lefty = tmp_df["ET_GazeLefty"].interpolate(method="linear")
        et_gaze_righty = tmp_df["ET_GazeRighty"].interpolate(method="linear")

        self.merged_data["ET_GazeRightx"] = et_gaze_rightx
        self.merged_data["ET_GazeLeftx"] = et_gaze_leftx
        self.merged_data["ET_GazeLefty"] = et_gaze_lefty
        self.merged_data["ET_GazeRighty"] = et_gaze_righty
        self.merged_data = self.merged_data.ffill()  # Forward fill
        self.merged_data = self.merged_data.bfill()  # Backward fill

        # Calculate average gaze position
        mean_gaze_x = self.merged_data[["ET_GazeRightx", "ET_GazeLeftx"]].mean(axis=1)
        mean_gaze_y = self.merged_data[["ET_GazeRighty", "ET_GazeLefty"]].mean(axis=1)

        self.merged_data["MeanGazeX"] = mean_gaze_x
        self.merged_data["MeanGazeY"] = mean_gaze_y
        self.merged_data.isnull().sum()  # check the null values

    def __split_data(self):
        # Split the data into different sections based on the URL

        self.split_data = self.merged_data.groupby("URL")
        # Iterate over the groups and save each group as a separate CSV file
        url_dataframes = []
        for _, group in self.split_data:
            # Save each group as a list of dataframes
            url_dataframes.append(group)
        return url_dataframes

    def plot_heatmap(self, screenshot_path):
        # Get the unique image path from the dataframe
        # img_path = data["Image_Path"].unique()[0]
        data = self.merged_data.copy()
        img = Image.open(screenshot_path)

        img_width, img_height = img.size

        # Calculate the normalized x and y coordinates
        P = data["Scroll Percentage"] / 100
        x = data["MeanGazeX"]
        y = abs(data["MeanGazeY"]) + (P * img_height)
        
        
        # Save count of the data points
        # png imagefile data type
        displayArray = np.empty([img_height, img_width])
        # Save count of the data points displayArray[y][x] = displayArray[y][x] + 1
        # get count of data points using enumerate
        
        for i in range(len(x)):
            try:
                displayArray[int(y[i])][int(x[i])] = displayArray[int(y[i])][int(x[i])] + 1
            except:
                pass
        smoothed = gaussian_filter(displayArray, sigma=50)
        
        plt.imshow(img, alpha=0.8)
        plt.axis("off")
        smoothed = gaussian_filter(displayArray, sigma=50)
        plt.imshow(smoothed, cmap="jet", alpha=.5)
        # remove the white space around the image

        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
       
        # save the plot as fig
        fig = plt.gcf()
        # return the plot
        return fig

    