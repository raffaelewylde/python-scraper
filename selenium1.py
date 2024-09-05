from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import requests
from urllib.parse import urljoin, urlparse

# Configuration
LOGIN_URL = "https://learnenough.com/login"
BASE_URL = "https://learnenough.com/"
DOWNLOAD_DIR = "./learnenough_content"
EMAIL = "learn@truenorthgnomes.info"  # Replace with your email/username
PASSWORD = "ham8yhm!RXJ3xqm2enc"  # Replace with your password
LOGIN_CHECK_ELEMENT = (
    By.LINK_TEXT,
    "Log Out",
)  # Replace with an element unique to logged-in users

# Initialize WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)


def login():
    driver.get(LOGIN_URL)

    try:
        # Wait for the CSRF token and login form to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "authenticity_token"))
        )
        csrf_token = driver.find_element(By.NAME, "authenticity_token").get_attribute(
            "value"
        )

        # Wait for the username field to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "user_login"))
        )
        driver.find_element(By.ID, "user_login").send_keys(EMAIL)

        # Wait for the password field to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "user_password"))
        )
        driver.find_element(By.ID, "user_password").send_keys(PASSWORD)

        # Submit the login form
        driver.find_element(By.NAME, "commit").click()

        # Wait for redirection to the expected post-login page
        WebDriverWait(driver, 20).until(
            EC.url_to_be("https://www.learnenough.com/your-courses")
        )

    except TimeoutException as e:
        print("Timeout occurred during login process.")
        print(f"Current URL: {driver.current_url}")
        raise e


def is_logged_in():
    try:
        driver.find_element(By.ID, LOGIN_CHECK_ELEMENT)
        return True
    except:
        return False


def download_file(url, download_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(download_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)


def clone_page(url):
    driver.get(url)

    # Ensure we are logged in
    if not is_logged_in():
        login()
        driver.get(url)  # Retry page load after login

    # Download page content
    page_source = driver.page_source
    page_path = os.path.join(DOWNLOAD_DIR, urlparse(url).path.lstrip("/"))
    os.makedirs(os.path.dirname(page_path), exist_ok=True)
    with open(page_path + ".html", "w", encoding="utf-8") as file:
        file.write(page_source)

    # Download media files (especially videos)
    videos = driver.find_elements(
        By.CSS_SELECTOR, "#vjs_video_3_html5_api.vjs_tech source"
    )
    for video in videos:
        video_url = video.get_attribute("src")
        video_name = os.path.basename(urlparse(video_url).path)
        download_file(video_url, os.path.join(DOWNLOAD_DIR, video_name))

    # Recursively clone linked pages
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute("href")
        if href and href.startswith(BASE_URL):
            clone_page(href)


def main():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    login()
    clone_page(BASE_URL)

    driver.quit()


if __name__ == "__main__":
    main()
