import os
import re
import time
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome import options
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://learnenough.com"
MID_URL = "/courses/"
MID_URL_LONG = "/courses/learn_enough_"
COURSE_URL_ENDINGS = ["command_line", "text_editor", "git", "html", "action_cable"]
ADDITIONAL_COURSE_URLS = ["css_and_layout", "javascript", "python", "ruby", "ruby_on_rail_tutorial_7th_edition", "ruby_on_rail_tutorial_6th_edition", "ruby_on_rail_tutorial_4th_edition"]
FULL_COURSE_URLS = [f"{BASE_URL}{MID_URL_LONG}{COURSE_URL_ENDING}" for COURSE_URL_ENDING in COURSE_URL_ENDINGS]
FULL_ADDITIONAL_COURSE_URLS = [f"{BASE_URL}{MID_URL_LONG}{ADDITIONAL_COURSE_URL}" for ADDITIONAL_COURSE_URL in ADDITIONAL_COURSE_URLS]
ALL_COURSE_URLS = FULL_COURSE_URLS + FULL_ADDITIONAL_COURSE_URLS
LOGIN_URL = f"{BASE_URL}/login"
DOWNLOAD_DIR = "my_selenium_downloads"
LOGIN = "learn@truenorthgnomes.info"
VIDEO_URLS = []
PASSWORD = "ham8yhm!RXJ3xqm2enc"
LOGIN_CHECK_ELEMENT = (
    By.LINK_TEXT,
    "Log Out",
)

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

def login():
    """
    This function logs into the LearnEnough website using the provided email and password.

    Parameters:
    None
    Returns:
    None

    The Function waits for the login form to load and then enters the provided email and password, 
    clicks the "Log In" button, and waits for the "Log Out" link to appear to confirm a succesful login.
    It prints a message indicating whether the login was successful or not.
    """
    try:
        driver.get(LOGIN_URL)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "user_login"))
        )
        driver.find_element(By.ID, "user_login").send_keys(LOGIN)
        driver.find_element(By.ID, "user_password").send_keys(PASSWORD)
        driver.find_element(By.NAME, "commit").click()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(LOGIN_CHECK_ELEMENT)
        )
        print("Login successful!")
    except TimeoutException:
        print("Login failed.")
def is_logged_in():
    """
    Checks if the user is logged in by looking for the presence of the "Log Out" link.
    Returns True if the "Log Out" link is found, False otherwise.
    global driver"""
    try:
        driver.find_element(By.ID, LOGIN_CHECK_ELEMENT)
        return True
    except:
        return False
    
def download_file(url, download_path):
    """
    Downloads a file from the given URL and saves it to the specified download_path.
    :param url: The URL of the file to download.
    :param download_path: The path where the file should be saved.
    :return: None"""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(download_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

def download_page_content(url):
    """
    Downloads the content of the given URL and writes it to a file in the specified download directory.
    :param url: The URL of the page to download.
    """
    # Download page content
    page_source = driver.page_source
    page_path = os.path.join(DOWNLOAD_DIR, urlparse(url).path.lstrip("/"))
    os.makedirs(os.path.dirname(page_path), exist_ok=True)
    with open(page_path + ".html", "w", encoding="utf-8") as file:
        file.write(page_source)

def download_images():
    """
    This function should download all images found on the current page and save them to the specified download directory.
    """
    try:
        image_elements = driver.find_elements(By.TAG_NAME, "img")
        for image_element in image_elements:
            image_url = image_element.get_attribute("src")
            if image_url:
                print(f"Image URL: {image_url}")
                download_file(image_url, os.path.join(DOWNLOAD_DIR, os.path.basename(image_url)))
    except NoSuchElementException:
        print("No image elements found on the page.")

def get_video_urls():
    """
    This function should return a list of video URLs found on the current page.
    :return: A list of video URLs
    """
    try:
        video_elements = driver.find_elements(By.TAG_NAME, "video")
        for video_element in video_elements:
            video_source = video_element.get_attribute("source")

            video_url = video_source.get_attribute("src")
            if video_url:
                print(f"Video URL: {video_url} added to video URLs list.")
                VIDEO_URLS.append(video_url)
        return VIDEO_URLS
    except NoSuchElementException:
        print("No video elements found on the page.")
        try:
            source = driver.page_source
            soup = BeautifulSoup(source, "html.parser")
            video_src_tag = soup.find("source", string=re.compile(r"mp4"))
            if video_src_tag:
                tag_content = video_src_tag.string
                link_match = re.search(r"^http://.*cloudfront.net.*[a-Z0-9]{20}$", tag_content)
                if link_match:
                    print(link_match)
                    print(link_match.group(0))
                    print(link_match.group(1))
                    video_url = link_match.group(1)
                    print(f"Found Video URL: {video_url} added to video URLs list.")
                    VIDEO_URLS.append(video_url)
        except NoSuchElementException:
            print("No video elements found on the page.")
def page_actions():
    current_url = driver.current_url
    download_page_content(current_url)
    get_video_urls()
    download_images()
    print(f"Downloaded page content for: {current_url}")
    print("=================================")


def main():
    login()
    for courseurl in ALL_COURSE_URLS:
        driver.get(courseurl)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "btn.btnSmall")))
        driver.find_element(By.CLASS_NAME, "btn.btnSmall").click()
        time.sleep(5)
        while True:
            try:
                page_actions()
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn.btnSmall")))
                driver.find_element(By.CLASS_NAME, "btn.btnSmall").click()
            except NoSuchElementException:
                print("This course/chapter has no more pages.")
    for video_url in VIDEO_URLS:
        download_file(video_url, os.path.join(DOWNLOAD_DIR, os.path.basename(video_url)))
        print(f"Downloaded: {video_url}")