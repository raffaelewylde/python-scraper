import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Configuration
base_url = "https://www.learnenough.com"  # Replace with the target website
login_url = urljoin(base_url, "/login")  # The login page URL
download_dir = "downloaded_site"
username = "abdenour@truenorthgnomes.info"  # Replace with your actual username or email
password = "daf*efw@BUA6mqk8fvp"  # Replace with your actual password

# Create session
session = requests.Session()


# Login
def login(session):
    # Get the login page to retrieve the CSRF token
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, "html.parser")

    # Retrieve CSRF token from the login form
    csrf_token = soup.find("input", {"name": "authenticity_token"})["value"]

    # Login payload
    payload = {
        "authenticity_token": csrf_token,
        "user[login]": username,
        "user[password]": password,
        "user[remember_me]": "1",  # Set to '1' to check "Remember me" by default
        "utf8": "✓",
    }

    # Post login request
    response = session.post(login_url, data=payload)
    if response.status_code == 200:
        print("Login successful!")
    else:
        print("Login failed!")
        exit()


# Function to download a file
def download_file(session, url, save_path):
    if os.path.exists(save_path):
        print(f"Already downloaded: {url}")
        return

    response = session.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded: {url}")
    else:
        print(f"Failed to download: {url}")


# Save HTML content
def save_html(session, url, save_path):
    if os.path.exists(save_path):
        print(f"Already saved HTML: {url}")
        return

    response = session.get(url)
    if response.status_code == 200:
        with open(save_path, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"Saved HTML: {url}")
    else:
        print(f"Failed to save HTML: {url}")


# Recursive function to scrape media files and HTML
def scrape_site(session, url, visited=set()):
    if url in visited:
        print(f"Already visited: {url}\n")
        return
    visited.add(url)
    print(f"Adding url to visited list: {url}\n")

    # Request page content
    response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Save the HTML file
    parsed_url = urlparse(url)
    print(f"the parsed URL is: {url}\n")
    html_path = os.path.join(
        download_dir, parsed_url.netloc, parsed_url.path.strip("/")
    )
    print(f"The HTML path is: {html_path}\n")
    if not html_path.endswith(".html"):
        html_path += ".html"
    print("We'll make this dir: " + os.path.dirname(html_path))
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    save_html(session, url, html_path)

    # Find and download CSS files
    for css in soup.find_all("link", {"rel": "stylesheet"}):
        css_url = css.get("href")
        if css_url:
            css_url = urljoin(url, css_url)
            css_path = urlparse(css_url).path
            print(f"The CSS path is: {css_path}\n")
            css_save_path = os.path.join(
                download_dir, parsed_url.netloc, css_path.strip("/")
            )
            print(f"The CSS save path is: {css_save_path}\n")
            os.makedirs(os.path.dirname(css_save_path), exist_ok=True)
            download_file(session, css_url, css_save_path)

    # Find and download media files
    media_links = soup.find_all(["img", "video", "audio", "source"])
    for media in media_links:
        media_url = media.get("src") or media.get("data-src")
        if media_url:
            media_url = urljoin(url, media_url)
            print(f"The media URL is: {media_url}\n")
            media_path = urlparse(media_url).path
            print(f"The media path is: {media_path}\n")
            save_path = os.path.join(
                download_dir, parsed_url.netloc, media_path.strip("/")
            )
            print(f"The media save path is: {save_path}\n")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            download_file(session, media_url, save_path)

    # Find and download video files
    for video in soup.find_all("video"):
        for source in video.find_all("source"):
            video_url = source.get("src")
            if video_url:
                video_url = urljoin(url, video_url)
                print(f"The video URL is: {video_url}\n")
                video_path = urlparse(video_url).path
                print(f"The video path is: {video_path}\n")
                save_path = os.path.join(
                    download_dir, parsed_url.netloc, video_path.strip("/")
                )
                print(f"The video save path is: {save_path}\n")
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                download_file(session, video_url, save_path)

    # Find and follow all internal links
    for link in soup.find_all("a", href=True):
        link_url = urljoin(url, link["href"])
        print(f"Following link: {link_url}\n")
        if base_url in link_url:
            scrape_site(session, link_url, visited)


# Main execution
if __name__ == "__main__":
    login(session)
    scrape_site(session, base_url)