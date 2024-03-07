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
import numpy as np
import cv2

import pandas as pd

BASE_COLUMNS = [
    "Timestamp",
    "Row",
    "StimType",
    "Duration",
    "SourceStimuliName",
    "CollectionPhase",
    "SlideEvent",
    "Participant",
    "SampleNumber",
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
    "GSR RAW",
    "GSR Resistance CAL",
    "GSR Conductance CAL",
    "Heart Rate PPG ALG",
    "GSR Raw",
    "GSR Interpolated",
    "Tonic Signal",
    "Phasic Signal",
]


class DataProcessor:
    """
    This class process iMotions data and generates several plots,
    its advantage against using off-the-shelf plots such as
    the ones included with iMotions is the possibility of
    working from a non-restrictive location, in other words
    no need of iMotions software other than generating the data,
    further analysis can be made in pure Python.
    """

    def __init__(self, imotions_path, images_path, output_path=None) -> None:
        self.imotions_path = imotions_path
        self.images_path = images_path
        self.output_path = output_path
        self.data_is_clean = False

    # TODO use the raw data to get the actual timestamp
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
        if not self.data_is_clean:
            raise ValueError("Clean the data first")
        dataframes = self.__load_clean_data()
        # Convert 'Timestamp' to datetime type and set it as index
        for _, df in dataframes.items():
            df["Timestamp"] = pd.to_datetime(df["Timestamp"])
            df.set_index("Timestamp", inplace=True)
        data = pd.DataFrame()
        for _, df in dataframes.items():
            data = pd.concat([data, df], axis=0)
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
        df.drop(
            columns=[col for col in columns_to_drop if col in df.columns], inplace=True
        )
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
                existing_columns = [
                    col for col in columns_to_keep if col in cleaned_df.columns
                ]

                # If any columns are missing, print a message or log it
                missing_columns = [
                    col for col in columns_to_keep if col not in cleaned_df.columns
                ]
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
        # First check if eye data is available
        # TODO add actual column names
        if not ['norm_x'] in data.columns:
            df['norm_x'] = np.random.normal(0.5, 0.1, len(df))
            df['norm_y'] = np.random.normal(0.5, 0.1, len(df))
        