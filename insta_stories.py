from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import selenium
import wget
import urllib.request
import sys, os, re, time
import subprocess
import requests
from os.path import basename
import shutil
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from zmatrix import Bot

# m = Bot('instagramApi')
# m.say('saysaysay')
# exit(0)

def filenameFromUrl(url):
    found = re.search(r'/home/instagram/stories/([^/]*)/([^/]*)', url)
    ms = int(round(time.time() * 1000))
    if found is not None:
        return 'users/{}/{}'.format(found.group(1), ms)
    return None

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--lang=de")
options.add_argument("--window-size=1920,1080")
options.add_argument('--user-agent=Mozilla/5.0 Chrome/74.0.3729.169 Safari/537.36')
options.add_experimental_option('prefs', {'intl.accept_languages': 'de_DE'})
driver = webdriver.Chrome(options=options)

css = {
        'storyItems': '.zGtbP.IPQK5.VideM .OE3OK',
        'storyOpen': 'ul.vi798 button.OE3OK',
        'storyItem': '.szopg video, .szopg img:not(._6q-tv)',
}

def acceptCookies():
    driver.find_element_by_xpath("//button[text()=\"Accept All\"]").click()

def login(myusername, mypassword, mode, accounts):
    driver.implicitly_wait(10)
    print("Logging in as " + '"' + myusername + '".')
    driver.get("https://www.instagram.com/accounts/login/")
    acceptCookies()
    driver.find_element_by_name('username').send_keys(myusername)
    driver.find_element_by_name('password').send_keys(mypassword)
    driver.find_element_by_css_selector("#loginForm button[type=\"submit\"]").click()
    driver.find_element_by_xpath("//button[text()=\"Not Now\"]").click()

    # Main loop of whole program
    scrapeStories()
    killMe()

def scrapeStories():
    #put links in arrays
    ImageList = []
    VideoList = []
    getSRCS(ImageList, VideoList)

def waitForUrlChange():
    before = driver.current_url
    WebDriverWait(driver, 60).until(lambda driver: driver.current_url != before)

def getSRCS(ImageList, VideoList):
    usernames = []

    urlBefore = driver.current_url
    driver.find_element_by_css_selector(css.get('storyOpen')).click()
    time.sleep(10)
    driver.get_screenshot_as_file("screenshot.png")

    while driver.current_url != urlBefore:
        for element in driver.find_elements_by_css_selector(css.get('storyItem')):
            filename = filenameFromUrl(driver.current_url)
            if element.tag_name == 'video':
                url = element.find_element_by_tag_name('source').get_attribute('src')
            if element.tag_name == 'img':
                url = element.get_attribute('src')

            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:
                    pass

            print('downloading')
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)
            
            print('download complete')
        waitForUrlChange()

def downloadInto(array, username):
    #Make folders for files
    cwd = os.getcwd()
    newpath = cwd + "\\" + username
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    # Download files into folder
    try:
        for i in range(len(array)):
            f_name = array[i].split('/')[10].split('?')[0]
            f_path_file = "./" + username + "/" + f_name
            my_file = Path(f_path_file)
            if my_file.is_file():
                print("File exsists...")
                continue
            else:
                # print(f_name)
                with requests.get(array[i], stream=True) as r:
                    r.raise_for_status()
                    with open(f_path_file, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk: # filter out keep-alive new chunks
                                f.write(chunk)
    except Exception as e:
        print(e)

def killMe():
    driver.close()
