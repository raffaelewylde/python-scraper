import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote

# Configuration
base_url = "https://www.learnenough.com"  # Replace with the target website
login_url = urljoin(base_url, "/login")  # The login page URL
download_dir = "selenium_downloaded"  # Replace with the desired download directory
download_url = "https://learnenough.com/your_courses"
download_urls = urljoin(base_url, "/your_courses")  # The download page URL
username = "learn@truenorthgnomes.info"  # Replace with your actual username or email
password = "ham8yhm!RXJ3xqm2enc"  # Replace with your actual password

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

    # Submit the form
    login_button.click()

    # Wait for the login to complete
    time.sleep(5)

    # Verify login success
    if "Log Out" not in driver.page_source:
        print("Login failed!")
        driver.quit()
        exit()
    else:
        print("Login successful!")


# Function to download a video file
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


# Function to decode HTML entities and save text content
def save_text_content(soup, save_path):
    # Find the text content in the desired div
    content_div = soup.find("div", {"class": "j_sectionContent"})
    if content_div:
        # Decode HTML entities
        decoded_text = unquote(content_div["data-html"])
        # Remove any remaining HTML tags
        soup_text = BeautifulSoup(decoded_text, "html.parser").get_text()

        with open(save_path, "w", encoding="utf-8") as file:
            file.write(soup_text)
        print(f"Saved text content: {save_path}")
    else:
        print(f"No text content found to save")

    time.sleep(20)  # Wait for 20 seconds before processing the next item


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

    # Determine the directory and filename from the URL
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    dir_name = path_parts[0] if path_parts else "root"
    file_name = path_parts[-1] if len(path_parts) > 1 else "index"

    # Ensure directory exists
    save_dir = os.path.join(download_dir, dir_name)
    os.makedirs(save_dir, exist_ok=True)

    # Save video files with a ".mp4" extension
    for video in soup.find_all("video"):
        for source in video.find_all("source", type="video/mp4"):
            video_url = source.get("src")
            if video_url:
                video_url = urljoin(url, video_url)
                save_path = os.path.join(save_dir, f"{file_name}.mp4")
                download_file(video_url, save_path)

    # Extract and save text content with a ".txt" extension
    save_text_path = os.path.join(save_dir, f"{file_name}.txt")
    save_text_content(soup, save_text_path)

    # Find and follow all internal links
    for link in soup.find_all("a", href=True):
        link_url = urljoin(url, link["href"])
        if base_url in link_url and link_url not in visited:
            scrape_site(link_url, visited)


# Main execution
if __name__ == "__main__":
    try:
        login()
        scrape_site(download_url)
    finally:
        driver.quit()
