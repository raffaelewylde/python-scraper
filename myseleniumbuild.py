import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome import options
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://learnenough.com"
MID_URL = "/courses/"
MID_URL_LONG = "/courses/learn_enough_"
COURSE_URL_ENDINGS = ["command_line", "text_editor", "git", "html", "action_cable"]
ADDITIONAL_COURSE_URLS = ["css_and_layout", "javascript", "python", "ruby", "ruby_on_rail_tutorial_7th_edition", "ruby_on_rail_tutorial_6th_edition", "ruby_on_rail_tutorial_4th_edition"]
FULL_COURSE_URLS = [f"{BASE_URL}{MID_URL_LONG}{COURSE_URL_ENDING}" for COURSE_URL_ENDING in COURSE_URL_ENDINGS]
FULL_ADDITIONAL_COURSE_URLS = [f"{BASE_URL}{MID_URL_LONG}{ADDITIONAL_COURSE_URL}" for ADDITIONAL_COURSE_URL in ADDITIONAL_COURSE_URLS]
ALL_COURSE_URLS = FULL_COURSE_URLS + FULL_ADDITIONAL_COURSE_URLS
LOGIN_URL = f"{BASE_URL}/login"
EMAIL = "learn@truenorthgnomes.info"
PASSWORD = "ham8yhm!RXJ3xqm2enc"
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
driver.get(LOGIN_URL)
driver.find_element(By.ID, "user_login").send_keys(EMAIL)
driver.find_element(By.ID, "user_password").send_keys(PASSWORD)
driver.find_element(By.NAME, "commit").click()
time.sleep(20)
for url in ALL_COURSE_URLS:
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "btn.btnSmall")))
    driver.find_element(By.CLASS_NAME, "btn.btnSmall").click()
    