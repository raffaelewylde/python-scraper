import time
import requests
from seleniumbase import BaseCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import os

class LearnEnoughScraper(BaseCase):
    base_url = "https://learnenough.com"
    login_url = "https://www.learnenough.com/login"
    session_cookie_name = "_polytexnic_session"
    videos_folder = "downloaded_videos"
    
    def setUp(self):
        super().setUp()
        self.login_credentials = {
            "username": "YOUR_USERNAME",  # Replace with your username
            "password": "YOUR_PASSWORD"   # Replace with your password
        }
        if not os.path.exists(self.videos_folder):
            os.makedirs(self.videos_folder)
    
    def login(self):
        """Logs into the site and maintains session."""
        self.open(self.login_url)
        csrf_token = self.get_attribute('input[name="authenticity_token"]', "value")
        
        self.type('input[name="user[login]"]', self.login_credentials['username'])
        self.type('input[name="user[password]"]', self.login_credentials['password'])
        self.set_attribute('input[name="authenticity_token"]', "value", csrf_token)
        
        self.click('input[type="submit"]')
        # Wait for login to complete by checking if logged-in element appears
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Log Out"))  # Adjust if the logout link is different
        )
        print("Logged in successfully!")
    
    def is_logged_in(self):
        """Checks if the session is still active."""
        cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
        response = requests.get(self.base_url, cookies=cookies)
        # Check if still logged in by inspecting page content or specific logged-in indicators
        return "Log Out" in response.text
    
    def check_and_login(self):
        """Ensures the user is logged in; re-logs in if needed."""
        if not self.is_logged_in():
            print("Session expired. Logging in again...")
            self.login()
        else:
            print("Already logged in.")
    
    def download_video(self, video_url):
        """Downloads the video file given its URL."""
        local_filename = os.path.join(self.videos_folder, os.path.basename(video_url))
        response = requests.get(video_url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded video: {local_filename}")
    
    def crawl_and_download(self, url):
        """Recursively crawls the website and downloads videos."""
        self.check_and_login()
        self.open(url)
        
        # Download any videos on the current page
        video_sources = self.find_elements('source[src*="cloudfront.net"]')
        for source in video_sources:
            video_url = source.get_attribute("src")
            self.download_video(video_url)
        
        # Find and follow links to other pages
        links = self.find_elements('a[href]')
        for link in links:
            href = link.get_attribute('href')
            if href and href.startswith(self.base_url):
                self.crawl_and_download(href)
    
    def test_recursive_download(self):
        """Main function to start the scraping and downloading process."""
        self.check_and_login()
        self.crawl_and_download(self.base_url)

if __name__ == "__main__":
    scraper = LearnEnoughScraper()
    scraper.setUp()
    try:
        scraper.test_recursive_download()
    finally:
        scraper.tearDown()
