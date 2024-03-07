"""
dataprocessor.py

This module contains the class DataProcessor, inspired by Mohammad,
Priyank and Sayidah's thesis. We present an OOP solution with well
documented methods and tested compatibility with iMotions 10, the
most recent version of iMotions.

Created on March 7th 2024 

Colchester, Essex.

"""

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

    