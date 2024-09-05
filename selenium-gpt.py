import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

# Path to your WebDriver
webdriver_path = 'C:\\Users\\jtaylor\\scoop\\shims\\chromedriver.exe'  # Set to the actual path of your WebDriver

# Your login credentials
username = "learn@truenorthgnomes.info"  # Replace with your actual username or email
password = "ham8yhm!RXJ3xqm2enc"  # Replace with your actual password

# Base URL for the website
base_url = 'https://learnenough.com'
download_urls = ["learnenough.com", "amazonaws.com", "cloudfront.net"]

# Initialize the Selenium WebDriver
driver = webdriver.Chrome(service=Service(webdriver_path))

def login():
    # Open the login page
    driver.get(f'{base_url}/login')

    # Find the login fields and input the credentials
    username_input = driver.find_element(By.NAME, "user[login]")
    password_input = driver.find_element(By.NAME, "user[password]")
    login_button = driver.find_element(By.NAME, "commit")

    # Enter login credentials
    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()

    # Wait for login to complete (adjust based on how long the site takes)
    time.sleep(10)

 # Verify login success
    if "Log Out" not in driver.page_source:
        print("Login failed!")
        driver.quit()
        exit()
    else:
        print("Login successful!")

def download_page_content(url, output_dir='cloned_site'):
    """Download the HTML and media content from the given page URL."""
    # Open the page
    driver.get(url)

    # Create a folder to store the site content
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the page source (HTML)
    page_name = url.split('/')[-1] or 'index'  # Use 'index' if the URL ends with '/'
    with open(f'{output_dir}/{page_name}.html', 'w', encoding='utf-8') as file:
        file.write(driver.page_source)

    print(f"Downloaded {url}")

def download_videos():
    """Download videos on the page if any are present."""
    video_elements = driver.find_elements(By.TAG_NAME, 'video')
    page_title = driver.title

    if video_elements:
        for i, video in enumerate(video_elements):
            # Find the source element for the video source
            source_element = video.find_element(By.TAG_NAME, 'source')
            video_src = source_element.get_attribute('src')
            if video_src:
                # Download the video content
                video_response = requests.get(video_src, stream=True)
                video_name = f'video_{page_title}_{i}.mp4'
                with open(f'videos/{video_name}', 'wb') as video_file:
                    for chunk in video_response.iter_content(chunk_size=1024):
                        video_file.write(chunk)
                print(f"Downloaded video: {video_name}")

def recursively_scrape(url, visited_urls=None, output_dir='cloned_site'):
    """Recursively scrape the site starting from a given URL."""
    if visited_urls is None:
        visited_urls = set()

    # Check if we've already visited this URL
    if url in visited_urls:
        print(f"We've already visited {visited_urls}")
        return

    # Mark the URL as visited
    visited_urls.add(url)

    # Download the page content
    download_page_content(url, output_dir)

    # Download videos if present
    download_videos()

    # Find all links on the page
    links = driver.find_elements(By.TAG_NAME, 'a')
    for link in links:
        href = link.get_attribute('href')
        if href and href.startswith(base_url) and href not in visited_urls:
            recursively_scrape(href, visited_urls, output_dir)

# Main execution
if __name__ == '__main__':
    try:
        # Log in to the website
        login()

        # Start the recursive scrape from the home page after login
        start_url = f'{base_url}/your-courses'
        recursively_scrape(start_url)

    finally:
        # Close the browser after scraping
        driver.quit()
