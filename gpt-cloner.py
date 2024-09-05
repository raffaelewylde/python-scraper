import os
import time
import requests
from bs4 import BeautifulSoup

# Configuration
base_url = "https://www.learnenough.com"  # Replace with the target website
login_url = urljoin(base_url, "/login")  # The login page URL
download_dir = "selenium_download"
username = "abdenour@truenorthgnomes.info"  # Replace with your actual username or email
password = "daf*efw@BUA6mqk8fvp"  # Replace with your actual password

# Create session
session = requests.Session()


# Login function
def login(session):
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, "html.parser")
    csrf_token = soup.find("input", {"name": "authenticity_token"})["value"]
    payload = {
        "authenticity_token": csrf_token,
        "user[login]": username,
        "user[password]": password,
        "user[remember_me]": "1",  # Set to '1' to check "Remember me" by default
        "utf8": "✓",
    }
    response = session.post(login_url, data=payload)
    if response.status_code == 200:
        print("Login successful!")
    else:
        print("Login failed!")
        exit()


# Function to check if logged in
def is_logged_in(session, url):
    response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    logout_link = soup.find("a", href="/sign_out")
    return logout_link is not None


# Function to download video files
def download_video(session, url, save_path):
    response = session.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded video: {url}")
    else:
        print(f"Failed to download video: {url}")
    time.sleep(120)


# Function to save text content
def save_text_content(session, url, save_path):
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text_content = soup.find(id="book").get_text(separator="\n", strip=True)
        text_content = unescape(text_content)
        with open(save_path, "w", encoding="utf-8") as file:
            file.write(text_content)
        print(f"Saved text content: {url}")
    else:
        print(f"Failed to save text content: {url}")
    time.sleep(120)


# Recursive function to scrape site
def scrape_site(session, url, visited=set()):
    if url in visited:
        return
    visited.add(url)

    # Check if still logged in
    if not is_logged_in(session, url):
        print("Session expired, logging in again...")
        login(session)

    response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Parse URL for naming files
    parsed_url = urlparse(url)
    base_path = os.path.join(
        download_dir, parsed_url.netloc, parsed_url.path.strip("/")
    )
    base_path = os.path.splitext(base_path)[0]  # Remove extension if any

    # Download video files
    video_sources = soup.find_all("video")
    for video in video_sources:
        source = video.find("source")
        if source and source.get("src"):
            video_url = urljoin(url, source.get("src"))
            video_path = f"{base_path}.mp4"
            os.makedirs(os.path.dirname(video_path), exist_ok=True)
            download_video(session, video_url, video_path)

    # Save text content
    text_path = f"{base_path}.txt"
    os.makedirs(os.path.dirname(text_path), exist_ok=True)
    save_text_content(session, url, text_path)

    # Find and follow all internal links
    for link in soup.find_all("a", href=True):
        link_url = urljoin(url, link["href"])
        if base_url in link_url:
            scrape_site(session, link_url, visited)


# Main execution
if __name__ == "__main__":
    login(session)
    scrape_site(session, base_url)
