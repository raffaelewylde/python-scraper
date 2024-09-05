import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Configuration
base_url = "https://www.learnenough.com"  # Replace with the target website
login_url = urljoin(base_url, "/login")  # The login page URL
download_dir = (
    "downloaded_selenium_files"  # Replace with the desired download directory"
)
username = "abdenour@truenorthgnomes.info"  # Replace with your actual username or email
password = "daf*efw@BUA6mqk8fvp"  # Replace with your actual password

# Set up WebDriver (this example uses Chrome)
driver = webdriver.Chrome()  # Make sure you have the correct driver installed


# Function to login to the site using Selenium
def login():
    driver.get(login_url)

    # Locate the username, password fields and login button
    username_input = driver.find_element(By.NAME, "user[login]")
    password_input = driver.find_element(By.NAME, "user[password]")
    login_button = driver.find_element(By.NAME, "commit")

    # Enter login credentials
    username_input.send_keys(username)
    password_input.send_keys(password)

    # Get CSRF token from the page
    csrf_token = driver.find_element(By.NAME, "authenticity_token").get_attribute(
        "value"
    )

    # Submit the form
    login_button.click()

    # Wait for the login to complete
    time.sleep(10)

    # Verify login success
    if "Log Out" not in driver.page_source:
        print("Login failed!")
        driver.quit()
        exit()
    else:
        print("Login successful!")


# Function to download a file
def download_file(url, save_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded: {url}")
    else:
        print(f"Failed to download: {url}")
    time.sleep(20)  # Wait for 20 seconds before downloading the next item


# Save HTML content
def save_html(url, save_path):
    page_source = driver.page_source
    with open(save_path, "w", encoding="utf-8") as file:
        file.write(page_source)
    print(f"Saved HTML: {url}")
    time.sleep(20)  # Wait for 120 seconds before processing the next item


# Recursive function to scrape the website
def scrape_site(url, visited=set()):
    if url in visited:
        return
    visited.add(url)

    # Navigate to the URL using Selenium
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Save the HTML file
    parsed_url = urlparse(url)
    html_path = os.path.join(
        download_dir, parsed_url.netloc, parsed_url.path.strip("/")
    )
    if not html_path.endswith(".html"):
        html_path += ".html"
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    save_html(url, html_path)

    # Download CSS files
    for css in soup.find_all("link", {"rel": "stylesheet"}):
        css_url = css.get("href")
        if css_url:
            css_url = urljoin(url, css_url)
            css_path = urlparse(css_url).path
            css_save_path = os.path.join(
                download_dir, parsed_url.netloc, css_path.strip("/")
            )
            os.makedirs(os.path.dirname(css_save_path), exist_ok=True)
            download_file(css_url, css_save_path)

    # Download media files (images, videos, etc.)
    for media in soup.find_all(["img", "audio", "source"]):
        media_url = media.get("src") or media.get("data-src")
        if media_url:
            media_url = urljoin(url, media_url)
            media_path = urlparse(media_url).path
            save_path = os.path.join(
                download_dir, parsed_url.netloc, media_path.strip("/")
            )
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            download_file(media_url, save_path)

    # Download video files explicitly (handling the provided example)
    for video in soup.find_all("video"):
        for source in video.find_all("source", type="video/mp4"):
            video_url = source.get("src")
            if video_url:
                video_url = urljoin(url, video_url)
                video_path = urlparse(video_url).path
                save_path = os.path.join(
                    download_dir, parsed_url.netloc, video_path.strip("/")
                )
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                download_file(video_url, save_path)

    # Find and follow all internal links
    for link in soup.find_all("a", href=True):
        link_url = urljoin(url, link["href"])
        if base_url in link_url and link_url not in visited:
            scrape_site(link_url, visited)


# Main execution
if __name__ == "__main__":
    try:
        login()
        scrape_site(base_url)
    finally:
        driver.quit()
