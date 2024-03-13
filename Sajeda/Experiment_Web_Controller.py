# ****************************** Import the libraries ***************************************************

# Built-in modules for working with file paths, system-specific parameters, and garbage collection
import os
import time
from datetime import datetime
from io import BytesIO
import warnings
import gc

# Libraries for file and directory dialogs
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

# Library for data manipulation and analysis
import pandas as pd

# Libraries for creating and manipulating arrays
import numpy as np

# Libraries for visualizations
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as colors
from scipy.stats import gaussian_kde


# Libraries for working with images
from PIL import Image,ImageTk

# Libraries for web scraping
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# Libraries for copying and moving files
import shutil

# Libraries for reading and writing CSV files
import csv

# Libraries for finding specific pathnames
import glob

# Libraries for statistical functions
import scipy.stats as stats

# Ignore warning messages to make output cleaner
warnings.filterwarnings('ignore')

# *************************************************** Start ********************************************************

def process_files(file_path1, file_path2, user_dir):

# ***************************************** Read the Data files *****************************************************
    # Read the Data from web
    web_data = pd.read_csv(file_path1, skiprows=1, names=['Time (UTC)', 
                            'Event', 'Scroll Position', 'Scroll Percentage', 'Mouse X', 'Mouse Y','URL'])
    
    # Read the data from iMotion 
    imotion_data = pd.read_csv(file_path2, skiprows=28) # skip the rows that in the data that dosn't have data 

# ***************************************** Directory for the websites screenshots ***********************************

    # Define the path to the existing screenshots folder of websites, change the path of the folder that have old images of websits
    existing_screenshots_folder = "C:\\Users\\sajed\\Desktop\\disseration files GUI\\Website EXP\\web_pages\\web_pages"

# ****************************************** Get the web Pages screenshots *******************************************
    # Get the unique URLs from the data
    unique_urls = web_data["URL"].unique()

    # Create the main output folder
    main_folder_name = os.path.join(user_dir, "web_pages")
    os.makedirs(main_folder_name, exist_ok=True)

    # Initialize the dataframe to store the output data
    output_data = pd.DataFrame(columns=['URL', 'Image_Path'])

    # loop through every url
    for url in unique_urls:
        # Create a subdirectory for the current URL if it doesn't exist
        url_folder_name = url.replace("https://", "").replace("/", "_")
        full_path = os.path.join(main_folder_name, url_folder_name)
        os.makedirs(full_path, exist_ok=True)
        
        # Define the screenshot path
        screenshot_path = os.path.join(full_path, "webpage_screenshot.png")

        # Flag to check if screenshot exists before in web pages folder and its subfolders
        screenshot_exists = False
        
        # Search for the screenshot in the existing web pages screenshots folder and its subfolders
        for dirpath, dirnames, filenames in os.walk(existing_screenshots_folder):
            for filename in filenames:
                if filename == "webpage_screenshot.png" and dirpath.endswith(url_folder_name):
                    existing_screenshot_path = os.path.join(dirpath, filename)
                    screenshot_exists = True
                    print(f"Screenshot matched at: {existing_screenshot_path}")  # Print matched file path

                    break  # If successful, break the loop
            if screenshot_exists:
                break      # If successful, break the loop

        # Check if the screenshot already exists in the existing screenshots folder
        if screenshot_exists:
            # Copy the existing screenshot to the new location
            shutil.copy(existing_screenshot_path, screenshot_path)
            output_data = pd.concat([output_data, pd.DataFrame([{'URL': url, 'Image_Path': screenshot_path}])], ignore_index=True)

            # Update the 'Image_path' column 
            url_mask = web_data['URL'] == url
            web_data.loc[url_mask, 'Image_Path'] = screenshot_path
            continue
        print("Screenshot does not exist before , will loading the page...")
        
        # Navigate to the webpage if the pages visted for the first time

        # Create a new instance of the Chrome driver 
        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--hide-scrollbars")

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)  # set the page load timeout
       
        for _ in range(5): # Retry 5 times before give up, some times due to the internet speed
            try:
                start_time = time.time()
                driver.get(url)
                end_time = time.time() # calculate the time taken by the page to load 
                print(f"Time taken to load {url}: {end_time - start_time} seconds")
                
                break  # If successful, break the loop
            except TimeoutException:
                print("Loading took too much time, retrying...")

        # Set the width and height of the browser window to the size of the whole document
        total_width = driver.execute_script("return document.body.offsetWidth")
        total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
        driver.set_window_size(total_width, total_height)

        # Capture the screenshot of the whole page
        screenshot = driver.get_screenshot_as_png()

        # Convert bytes to Image
        screenshot_img = Image.open(BytesIO(screenshot))

        # Save the screenshot in the subfolder for unique user
        screenshot_path = os.path.join(full_path, "webpage_screenshot.png")
        screenshot_img.save(screenshot_path)

        # save the new screenshot for the main folder for web pages for future use
        full_path_old = os.path.join(existing_screenshots_folder, url_folder_name)
        os.makedirs(full_path_old, exist_ok=True)
        screenshot_path_2 = os.path.join(full_path_old, "webpage_screenshot.png")
        screenshot_img.save(screenshot_path_2)

        # Close the browser
        driver.quit()

        # Add the URL and image path to the output data
        # output_data = output_data.append({'URL': url,'Image_Path': screenshot_path}, ignore_index=True) # append is not working with some of python version 
        output_data = pd.concat([output_data, pd.DataFrame([{'URL': url, 'Image_Path': screenshot_path}])], ignore_index=True)

        # Update the 'Image_path' column 
        url_mask = web_data['URL'] == url
        web_data.loc[url_mask, 'Image_Path'] = screenshot_path

    # Save the output data to a CSV file
    output_data.to_csv(os.path.join(main_folder_name, "screenshot_data.csv"), index=False)

    # ******************* Web data processing ***********************************************

    # Replace NaN with 0 only at the beginning of each url sequence
    web_data.reset_index(drop=True, inplace=True)
    web_data['Scroll Percentage'] = web_data.groupby((web_data['URL'] != web_data['URL'].shift()).cumsum())['Scroll Percentage'].apply(lambda group: group.fillna(0, limit=1)).reset_index(drop=True)

    # Fill other NaN values (not at the start of a sequence) with the last valid observation forward to next valid
    web_data['Scroll Percentage'].fillna(method='ffill', inplace=True)

    # fill the null for the web data 
    web_data['Scroll Position'].fillna(method='ffill', inplace=True)
    web_data['Scroll Position'].fillna(method='bfill', inplace=True)
    web_data['Mouse X'].fillna(method='ffill', inplace=True)
    web_data['Mouse X'].fillna(method='bfill', inplace=True)
    web_data['Mouse Y'].fillna(method='ffill', inplace=True)
    web_data['Mouse Y'].fillna(method='bfill', inplace=True)
    web_data

    # save the web data to a csv file 
    web_data.to_csv(os.path.join(main_folder_name, "web_data_filled.csv"), index=False)

    # ******************* iMotion Data processing ***********************************************
    gaze_data = imotion_data[1:-2] 
    gaze_data = gaze_data.loc[~(gaze_data["ET_GazeRightx"]==-1)].reset_index(drop=True)
    gaze_data = gaze_data[["Timestamp","Anger","Fear","Joy","Sadness","Surprise",
                        "Engagement","Confusion","Neutral","ET_GazeRightx","ET_GazeLeftx","ET_GazeLefty",
                        "ET_GazeRighty"]]

    # Convert the "Timestamp" column to datetime format with milliseconds
    gaze_data['Timestamp'] = pd.to_datetime(gaze_data['Timestamp'], unit='ms', utc=True)

    # Convert the datetime format to string with milliseconds
    gaze_data['Timestamp'] = gaze_data['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S.%f')
    eye_tracking_data= gaze_data.copy()

    # ********************************** Merge the web Data to iMotion data to get only one data frame *********************

    # Make sure the timestamps are in datetime format
    web_data['Time (UTC)'] = pd.to_datetime(web_data['Time (UTC)'])
    eye_tracking_data['Timestamp'] = pd.to_datetime(eye_tracking_data['Timestamp'])

    # Calculate the time difference for the 'eye_tracking_data' from its start
    eye_tracking_data['Time From Start'] = eye_tracking_data['Timestamp'] - eye_tracking_data['Timestamp'].iloc[0]

    # Apply this difference to the 'web_data' timestamps
    eye_tracking_data['Aligned Timestamp'] = web_data['Time (UTC)'].iloc[0] + eye_tracking_data['Time From Start']

    # If you don't need the original timestamps or the 'Time From Start' in your final dataframe, you can drop them
    eye_tracking_data.drop(['Timestamp', 'Time From Start'], axis=1, inplace=True)

    # Make the 'Aligned Timestamp' the index of 'eye_tracking_data'
    eye_tracking_data.set_index('Aligned Timestamp', inplace=True)

    # Make 'Time (UTC)' the index of 'web_data'
    web_data.set_index('Time (UTC)', inplace=True)

    # Now merge both dataframes on nearest matching time
    merged_data = pd.merge_asof(web_data, eye_tracking_data, left_index=True, right_index=True, direction='nearest')

    merged_data.reset_index(inplace=True)
    merged_data

    # **************************** Merged Data pre-processing ********************************************************
    merged_data['ET_GazeRightx'].interpolate(method='linear', inplace=True)
    merged_data['ET_GazeLeftx'].interpolate(method='linear', inplace=True)
    merged_data['ET_GazeLefty'].interpolate(method='linear', inplace=True)
    merged_data['ET_GazeRighty'].interpolate(method='linear', inplace=True)
    merged_data = merged_data.ffill() # Forward fill
    merged_data = merged_data.bfill() # Backward fill

    # Calculate average gaze position
    merged_data['MeanGazeX'] = merged_data[['ET_GazeRightx', 'ET_GazeLeftx']].mean(axis=1)
    merged_data['MeanGazeY'] = merged_data[['ET_GazeRighty', 'ET_GazeLefty']].mean(axis=1)
    merged_data.isnull().sum() # check the null values

    # merged_data.to_csv('merged_data.csv', index=False)
    merged_data.to_csv(os.path.join(user_dir, 'merged_data.csv'), index=False)

    # ********************Split the data based on the unique URLs ******************************************
    # get a dictionary for the split based on the URL
    data_dict = {url: df for url, df in merged_data.groupby('URL')}

    # Create a new directory to store the split data
    os.makedirs(os.path.join(user_dir, "url_datasets"), exist_ok=True)

    # Iterate over the dictionary and save each DataFrame as a separate CSV file
    for url, df in data_dict.items():
        # Create a valid file name from the URL
        filename = url.replace('https://', '').replace('/', '_') + '.csv'
        
        # Save the DataFrame as a CSV file
        df.to_csv(os.path.join(user_dir, f'url_datasets/{filename}'), index=False)

    #************************************ Creating Heatmap ************************************************

    def create_heatmap(d, csv_file, user_dir):
        print(f"Processing URL: {csv_file}")  # add the print statement here

        # Define the directory where you want to save the images
        output_dir = os.path.join(user_dir, "output_scatter_full_web_images")

        # If the directory doesn't exist, create it
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Get the unique image path from the dataframe
        img_path = d['Image_Path'].unique()[0]
        print(img_path)
        

        # Load screenshot as image
        img = Image.open(img_path)
        img_width, img_height = img.size

        # Calculate the normalized x and y coordinates
        P = d['Scroll Percentage'] / 100
        x = d['MeanGazeX']
        y = abs(d['MeanGazeY']) + (P * img_height)
        print(x.min())

        # Compute the point densities
        xy = np.vstack([x, y])
        z = gaussian_kde(xy)(xy)

        # Create the plot
        fig, ax = plt.subplots()
        ax.imshow(img, extent=[0, img_width, img_height, 0])

        # scatter the data and set the parameters 
        sc= ax.scatter(
        x, y, 
        s=500,                 # size of markers
        c=z,                   # color based on densities
        cmap='RdYlGn_r',       # colormap from red to green
        alpha=0.05,            # transparency
        marker='o',            # marker shape
        # edgecolors='black',  # edge color of markers
        linewidths=1.5         # edge line width
        )
        # Adjusted position and size for the colorbar at the top
        # cbar_ax_top = fig.add_axes([0.6, 0.96, 0.02, 0.01])  # [left, bottom, width, height]
                                   
        # # Add a colorbar at the top with horizontal orientation
        # cbar = fig.colorbar(sc, cax=cbar_ax_top, orientation='horizontal')
        ax.set_xlim(x.min(), img_width)
        ax.set_ylim(img_height, 0)
        ax.axis('off') 

        # Remove the boundries  
        plt.tight_layout()
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.gca().set_axis_off()
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())

        # Use the CSV file name to create a subdirectory
        subdirectory = csv_file.replace('.', '_')
        os.makedirs(os.path.join(output_dir, subdirectory), exist_ok=True)
        # Create the output path for the image
        # output_path = os.path.join(output_dir, subdirectory, 'heatmap_' + img_path.split('/')[-1])
        output_path = os.path.join(output_dir, subdirectory, 'heatmap_' + img_path.split('\\')[-1])
        # Save the figure before displaying it
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        # Close the figure to free up memory
        plt.close(fig)
        print(f"Saving heatmap image at: {output_path}")
        return [output_path]


    # get the data files in the folder that have all the data set for each URL
    csv_files = [file for file in os.listdir(os.path.join(user_dir, "url_datasets")) if file.endswith('.csv')]
    
    # Initialize an empty list to store all output paths
    output_paths = []  

    # Iterate over the CSV files
    for csv_file in csv_files:
        # Load the data from the CSV file
        df = pd.read_csv(os.path.join(user_dir, "url_datasets", csv_file))

        # Create a heatmap using the data
        output_paths.extend(create_heatmap(df, csv_file, user_dir))  # use extend, not append
    
    return output_paths 

# *************************************** Display the heatmaps on GUI ****************************************

def display_images(image_paths, frame3=None, display_frame=None):
    if not display_frame:
            display_frame = frame3  # default frame for displaying images

    for widget in display_frame.winfo_children():
        widget.destroy()
    images_per_row = 5  # defined 5 images to show in the screen 
    for i, image_path in enumerate(image_paths):
        with Image.open(image_path) as img:
            maxsize = (1024, 1024)
            img.thumbnail(maxsize)
            photo_img = ImageTk.PhotoImage(img)  
            row = i // images_per_row
            col = i % images_per_row
            label = tk.Label(display_frame, image=photo_img)
            label.image = photo_img
            label.grid(row=row, column=col)



