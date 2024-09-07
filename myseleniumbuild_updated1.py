import os
import time
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://learnenough.com"
LOGIN_URL = f"{BASE_URL}/login"
DOWNLOAD_DIR = "LearnEnoughSeleniumContent-Sept_6"
LOGIN = "learn@truenorthgnomes.info"
PASSWORD = "ham8yhm!RXJ3xqm2enc"

# Constants for button selectors
NEXT_BUTTON_SELECTOR = ".btn.btnSmall"
ATTENTION_BUTTON_SELECTOR = ".btn.attention"

options = webdriver.ChromeOptions()
options.timeouts = {"implicit": 10000, "pageLoad": 15000, "script": 15000}
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


def download_file(url, download_path):
    """Downloads a file from the given URL."""
    with requests.Session() as session:
        response = session.get(url, stream=True)
        if response.status_code == 200:
            with open(download_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)


def download_page_content(url):
    """Downloads the content of the given URL."""
    page_source = driver.page_source
    page_path = os.path.join(DOWNLOAD_DIR, urlparse(url).path.lstrip("/"))
    os.makedirs(os.path.dirname(page_path), exist_ok=True)
    with open(page_path + ".html", "w", encoding="utf-8") as file:
        file.write(page_source)


def download_images(page_url):
    """Downloads all images found on the current page."""
    page_path = os.path.join(DOWNLOAD_DIR, urlparse(page_url).path.lstrip("/"))
    os.makedirs(os.path.dirname(page_path), exist_ok=True)
    image_elements = driver.find_elements(By.TAG_NAME, "img")
    for image_element in image_elements:
        image_url = image_element.get_attribute("src")
        if image_url:
            image_name = os.path.basename(urlparse(image_url).path)
            image_path = os.path.join(os.path.dirname(page_path), image_name)
            download_file(image_url, image_path)


def page_actions():
    """Performs actions on the current page."""
    current_url = driver.current_url
    download_page_content(current_url)
    download_images(current_url)


def main():
    """Main function to execute the downloader."""
    login()
    # Assuming ALL_COURSE_URLS is defined earlier
    for course_url in ALL_COURSE_URLS:
        driver.get(course_url)
        page_text = BeautifulSoup(driver.page_source, "html.parser").get_text().lower()
        if "congratulations" in page_text:
            attention_button = driver.find_elements(
                By.CSS_SELECTOR, ATTENTION_BUTTON_SELECTOR
            )
            while True:
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, NEXT_BUTTON_SELECTOR)
                        )
                    )
                    next_button.click()
                    page_actions()
                except (TimeoutException, NoSuchElementException):
                    break
                time.sleep(5)

    driver.quit()


if __name__ == "__main__":
    main()
