import os
import sys
import asyncio
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


async def init_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Run in headless mode
    options.add_argument("--log-level=3")
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    # driver.add_cookie(cookie)
    return driver


async def load_page(driver, player_id, player):
    try:
        loop = asyncio.get_event_loop()
        # Running driver.get() in a thread
        await loop.run_in_executor(None, driver.get, FBREF + f"players/{player_id}/{player.replace(' ','-')}")

        # Wait for the first element
        await loop.run_in_executor(None, WebDriverWait(driver, 10).until, EC.visibility_of_element_located((By.ID, 'stats_standard_dom_lg')))
        
        # Wait for the second element
        await loop.run_in_executor(None, WebDriverWait(driver, 10).until, EC.visibility_of_element_located((By.ID, 'stats_playing_time_dom_lg')))
        
        page_source = driver.page_source

        return page_source
    
    except TimeoutException as e:
            print(f' Error finding table: {e}')
            sys.exit()
    except Exception as e:
            print(e)
            sys.exit()