import os
import time
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://learnenough.com"
LOGIN_URL = f"{BASE_URL}/login"
DOWNLOAD_DIR = "LearnEnoughSeleniumContent-Sept_6"
LOGIN = "learn@truenorthgnomes.info"
PASSWORD = "ham8yhm!RXJ3xqm2enc"

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)


def login():
    """Logs into the LearnEnough website."""
    driver.get(LOGIN_URL)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "user_login"))
    )
    driver.find_element(By.ID, "user_login").send_keys(LOGIN)
    driver.find_element(By.ID, "user_password").send_keys(PASSWORD)
    driver.find_element(By.NAME, "commit").click()
    time.sleep(5)


def download_file(url):
    """Downloads a file from the given URL."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        file_name = os.path.basename(urlparse(url).path)
        download_path = os.path.join(DOWNLOAD_DIR, file_name)
        with open(download_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded: {file_name}")


def download_images(page_url):
    """Downloads all images found on the current page."""
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    image_elements = soup.find_all("img")

    with ThreadPoolExecutor() as executor:
        for image_element in image_elements:
            image_url = image_element.get("src")
            if image_url:
                executor.submit(download_file, image_url)


def download_videos(page_url):
    """Downloads all videos from the current page."""
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    video_source_tags = soup.find_all("source")

    with ThreadPoolExecutor() as executor:
        for video_src_tag in video_source_tags:
            video_url = video_src_tag.get("src")
            if video_url:
                executor.submit(download_file, video_url)


def page_actions():
    """Performs actions on the current page."""
    current_url = driver.current_url
    download_images(current_url)
    download_videos(current_url)
    print(f"Processed page: {current_url}")


def main():
    login()  # Log in to the site
    # Assuming ALL_COURSE_URLS is defined earlier
    for course_url in ALL_COURSE_URLS:
        print(f"Attempting to navigate to {course_url}...")
        driver.get(course_url)
        page_actions()
        # Logic for navigating through pages can go here

    driver.quit()  # Close the driver after operations are complete


if __name__ == "__main__":
    main()
