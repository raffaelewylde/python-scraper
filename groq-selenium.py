import os
import re
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://learnenough.com"
MID_URL = "/courses/"
MID_URL_LONG = "/course/learn_enough_"
COURSE_URL_ENDINGS = [
    "command_line",
    "text_edior",
    "git",
    "html",
    "css",
    "javascript",
    "python",
    "ruby",
    "ruby_on_rail_tutorial_7th_edition",
    "ruby_on_rail_tutorial_6th_edition",
    "ruby_on_rail_tutorial_4th_edition",
    "action_cable",
]
URL_END = "/frontmatter"
ADDITIONAL_COURSE_URLS = [
    "css",
    "javascript",
    "python",
    "ruby",
    "ruby_on_rail_tutorial_7th_edition",
    "ruby_on_rail_tutorial_6th_edition",
    "ruby_on_rail_tutorial_4th_edition",
]
FULL_COURSE_URLS = [f"{BASE_URL}{MID_URL_LONG}{course_url_ending}" for course_url_ending in COURSE_URL_ENDINGS]
FULL_ADDITIONAL_COURSE_URLS = [f"{BASE_URL}{MID_URL}{additional_course_url}" for additional_course_url in ADDITIONAL_COURSE_URLS]
ALL_COURSE_URLS = [f"{BASE_URL}{MID_URL_LONG}{course_url_ending}{URL_END}" for course_url_ending in COURSE_URL_ENDINGS]
LOGIN_URL = f"{BASE_URL}/login"
DOWNLOAD_DIR = "LearnEnoughSeleniumContent-Sept_6"
LOGIN = "learn@truenorthgnomes.info"
PASSWORD = "ham8yhm!RXJ3xqm2enc"
options = Options()
options.timeouts = {"implicit": 10000, "pageLoad": 15000, "script": 15000}
driver = webdriver.Chrome(options=options)

def login():
    try:
        driver.get(LOGIN_URL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "user_login")))
        driver.find_element(By.ID, "user_login").send_keys(LOGIN)
        driver.find_element(By.ID, "user_password").send_keys(PASSWORD)
        driver.find_element(By.NAME, "commit").click()
        time.sleep(5)
    except TimeoutException:
        print("Timed out waiting for the login form to load.")

def download_file(url, download_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(download_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

def download_page_content(url):
    page_source = driver.page_source
    page_path = os.path.join(DOWNLOAD_DIR, urlparse(url).path.lstrip("/"))
    os.makedirs(os.path.dirname(page_path), exist_ok=True)
    with open(page_path + ".html", "w", encoding="utf-8") as file:
        file.write(page_source)

def download_images(page_url):
    try:
        page_path = os.path.join(DOWNLOAD_DIR, urlparse(page_url).path.lstrip("/"))
        os.makedirs(os.path.dirname(page_path), exist_ok=True)
        image_elements = driver.find_elements(By.TAG_NAME, "img")
        for image_element in image_elements:
            image_url = image_element.get_attribute("src")
            if image_url:
                image_name = os.path.basename(urlparse(image_url).path)
                image_path = os.path.join(os.path.dirname(page_path), image_name)
                print(f"Image URL: {image_url}")
                download_file(image_url, image_path)
    except NoSuchElementException:
        print("No image elements found on the page.")

def download_videos(page_url):
    try:
        page_path = os.path.join(DOWNLOAD_DIR, urlparse(page_url).path.lstrip("/"))
        os.makedirs(os.path.dirname(page_path), exist_ok=True)
        source = driver.page_source
        soup = BeautifulSoup(source, "html.parser")
        video_source_tags = soup.find_all("source")
        for video_src_tag in video_source_tags:
            video_url = video_src_tag.get("src")
            if video_url:
                video_name = os.path.basename(urlparse(video_url).path)
                video_path = os.path.join(os.path.dirname(page_path), video_name)
                print(f"Downloading video: {video_url} to {video_path}")
                download_file(video_url, video_path)
    except NoSuchElementException:
        print("No video elements found on the page.")

def page_actions():
    current_url = driver.current_url
    download_page_content(current_url)
    download_videos(current_url)
    download_images(current_url)
    print(f"Downloaded page content, images and video for: {current_url}")
    print("=================================")
    print("=================================")

def navigate_courses():
    for course_url in ALL_COURSE_URLS:
        print(f"Attempting to navigate to {course_url}...")
        driver.get(course_url)
        pgsource = driver.page_source
        soup = BeautifulSoup(pgsource, "html.parser")
        page_text = soup.get_text().lower()
        word_to_search = "congratulations"
        attention_button = None

        if word_to_search in page_text:
            try:
                attention_button = driver.find_element(By.CSS_SELECTOR, ".btn.attention")
            except NoSuchElementException:
                print("Attention button not found.")

        while True:
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btnSmall"))
                )
                next_button.click()
                page_actions()
                time.sleep(5)
            except TimeoutException:
                print("Next button is not clickable or found.")
                break
            except NoSuchElementException:
                print("This course/chapter has no more pages.")
                break

            if attention_button and attention_button.is_displayed():
                print("Attention button is displayed.")
                break

def main():
    login()
    navigate_courses()
    for video_url in VIDEO_URLS:
        download_file(video_url, os.path.join(DOWNLOAD_DIR, os.path.basename(video_url)))
        print(f"Downloaded: {video_url}")
    driver.quit()

if __name__ == "__main__":
    main()
