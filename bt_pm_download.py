from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re
import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import TimeoutException
#ActionChains(driver).move_to_element(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'accept-cookie-consent')))).click().perform()

def waited_find(by, desc):
    wait = WebDriverWait(driver, 10)
    by = by.upper()
    if by == 'XPATH':
        wait.until(EC.element_to_be_clickable((By.XPATH, desc)))
    if by == 'ID':
        wait.until(EC.element_to_be_clickable((By.ID, desc)))
    if by == 'LINK_TEXT':
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, desc)))

def get_release_urls(html, base=''):
    soup = BeautifulSoup(html, features='html5lib')
    releases = soup.find_all('a', href=True, class_='bt-link-intern bt-open-in-overlay')
    release_urls = [base + release['href'] + '\n' for release in releases]
    return release_urls

## Configure webdriver instance
options = webdriver.ChromeOptions()
options.add_argument('headless')
#options.add_argument("start-maximized")
#options.add_argument("window-size=1440,900")

## Initialize WebDriver (headless chrome)
driver = webdriver.Chrome(options=options)

driver.maximize_window()

## Wait for page to load: 60 seconds
driver.implicitly_wait(120)

## Load URL
base = 'https://www.bundestag.de'

for year in range(2016, 2020):
    ## Set up list for urls of releases
    pressrelease_urls = []
    
    driver.get( base + '/webarchiv/presse/pressemitteilungen/' + str(year))
    
    ## Get screenshot for debugging
    driver.save_screenshot('screenshot_open_' + str(year) + '.png')
    
    ## Parse urls
    pressrelease_urls.extend(get_release_urls(driver.page_source, base))
    
    xpath = '//*[contains(concat( " ", @class, " " ), concat( " ", "icon-angle-right", " " ))]'
    
    ## Find Button for next page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    ## Get screenshot for debugging
    driver.save_screenshot('screenshot_scrolled_' + str(year) + '.png')
    
    button = WebDriverWait(driver, 90).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    
    while button.is_displayed():
        ## Click the button
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(round(random.uniform(1.,3.), 2))
        button.click()
        print('\n--clicked--\n')
        ## Parse urls
        time.sleep(round(random.uniform(5.,10.), 2))
        data = get_release_urls(driver.page_source, base)
        print(data)
        pressrelease_urls.extend(data)
        ## Find Button for next page again
        try:
            button = WebDriverWait(driver, 90).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        except TimeoutException:
            driver.save_screenshot('screenshot_last_' + str(year) + '.png')
            break
    
    with open('urls_' + str(year) +'.txt', 'w') as f:
        f.writelines(pressrelease_urls)

# Download with wget
