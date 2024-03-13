"""
webpagecapture.py

This module contains the WebPageCapture class, which is used to capture 
screenshots and HTML of webpages using the Chrome webdriver.

February 2024

"""
import time
from io import BytesIO

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


class WebPageCapture:
    """
    WebPageCapture is a class that is used to capture
    screenshots and HTML of webpages using the Chrome webdriver.
    """

    def __init__(self, chrome_driver_path, window_size=(1920, 1080)):
        """
        ----
        Args:
        ----
        chrome_driver_path (str): The path to the Chrome webdriver executable.
        window_size (tuple): The size of the browser window, in the format (width, height).
        """
        self.chrome_driver_path = chrome_driver_path
        self.window_size = window_size

    def get_chrome_options(self):
        """Helper function to get the Chrome options for the webdriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(
            f"--window-size={self.window_size[0]},{self.window_size[1]}"
        )
        # capture the entire webpage
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-gpu")
        

        return chrome_options

    def start_chrome_driver(self):
        """Helper function to start the Chrome webdriver."""
        chrome_options = self.get_chrome_options()
        service = webdriver.ChromeService(executable_path=self.chrome_driver_path)
        driver = webdriver.Chrome(service=service)
        driver.options = chrome_options
        return driver

    def capture_screenshot(self, url: str):
        """
        Capture a screenshot of a webpage using the Chrome webdriver.
        Args:
        url (str): The URL of the webpage to capture.
        Returns:
        Image: The screenshot of the webpage as a PIL Image object.
        """
        driver = self.start_chrome_driver()
        driver.set_page_load_timeout(60)  # set the page load timeout

        for _ in range(5):  # Retry up to 5 times
            try:
                start_time = time.time()
                driver.get(url)
                end_time = time.time()
                print(f"Time taken to load {url}: {end_time - start_time} seconds")
                break
            except TimeoutException:
                print("Loading took too much time, retrying...")
        # Set the width and height of the browser window to the size of the whole document
        # Use JavaScript to get the full width and height of the webpage
        total_width = driver.execute_script("return Math.max( document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth );")
        total_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")

        driver.set_window_size(total_width, total_height)
        full_page = driver.find_element(By.TAG_NAME, "body")
        screenshot_bytes = full_page.screenshot_as_png()
        # Optionally, convert bytes to Image for manipulation or viewing
        screenshot_img = Image.open(BytesIO(screenshot_bytes))
        driver.quit()
        return screenshot_img

    def capture_html(self, url, output_path):
        """
        Capture the HTML of a webpage using the Chrome webdriver.
        Args:
        url (str): The URL of the webpage to capture.
        output_path (str): The path to save the HTML to.
        Returns:
        None
        """
        driver = self.start_chrome_driver()
        driver.get(url)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(driver.page_source)
        driver.quit()
