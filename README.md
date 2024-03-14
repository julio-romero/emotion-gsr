# Overview

Python application that acts as a graphical user interface (GUI) for managing experiments related to emotion analysis using data from iMotions. It integrates the work of multiple developers, each contributing different modules for analyzing emotions from websites, images, and videos. 

# Usage 

In order to run this application you will need to install the requirements.

```bash
pip install -r requirements.txt
```

Then you can initialize the app with

```bash
python app.py
```

# Project Structure

```bash
.
├── LICENSE
├── README.md
├── app.py
├── emotiongsr
│   ├── __init__.py
│   └── dataprocessor.py
├── images_app.py
├── multimotions
│   └── dataprocessor.py
├── requirements.txt
├── sample_data
│   ├── CleanedData
│   ├── Data
│   ├── Images
│   └── WebData
├── videos_app.py
└── websites_app.py
```
