import requests
from bs4 import BeautifulSoup
import os
import re

# Set the base URL and the paths to scrape
base_url = "https://learnenough.com"
login_url = f"{base_url}/login"
course_urls = [f"{base_url}/your-courses", f"{base_url}/course/"]
download_directory = "files_downLoaded"

# User credentials (replace with your actual credentials)
username = "learn@truenorthgnomes.info"
password = "ham8yhm!RXJ3xqm2enc"

# Session to maintain cookies and session data
session = requests.Session()


# Function to log in to the website
def login():
    # Get login page to extract the CSRF token
    response = session.get(login_url)
    soup = BeautifulSoup(response.content, "html.parser")
    csrf_token = soup.find("input", {"name": "authenticity_token"})["value"]

    # Create login data payload
    login_data = {
        "user[login]": username,
        "user[password]": password,
        "authenticity_token": csrf_token,
        "commit": "Log in",
    }

    # Post login data to the login URL
    response = session.post(login_url, data=login_data)

    # Get Auth Cookie
    auth_cookie = response.cookies.get("auth_cookie")

    if response.status_code == 200 and "Your Courses" in response.text:
        print("Logged in successfully.")

    if response.status_code == 200 and "Your Courses" in response.text:
        print("Logged in successfully.")
    if response.status_code == 200 and "Your Courses" in response.text:
        print("Logged in successfully.")
    else:
        print("Failed to log in.")
        exit()


# Function to check if still logged in
def check_login():
    # Test by accessing a protected page
    response = session.get(course_urls[0])
    if "Log In" in response.text:
        print("Session expired. Logging in again.")
        login()
    else:
        print("Session is still active.")


# Function to recursively scrape and download content
def scrape_and_download(url):
    response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find and download video files
    video_sources = soup.find_all("source", src=re.compile(r"cloudfront.net"))
    for video_source in video_sources:
        video_url = video_source["src"]
        print(video_url)
        download_media(video_url)

    # Find all internal links to follow
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith(base_url):
            print(href)
            scrape_and_download(href)
        elif href.startswith("/"):
            print(href)
            scrape_and_download(f"{base_url}{href}")


# Function to download media files
def download_media(url):
    local_filename = url.split("/")[-1]
    os.makedirs(download_directory, exist_ok=True)
    save_path = os.path.join(download_directory, local_filename)
    with session.get(url, stream=True) as r:
        r.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded {save_path}")


# Main script execution
if __name__ == "__main__":
    login()

    for course_url in course_urls:
        check_login()
        scrape_and_download(course_url)
