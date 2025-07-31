#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Hide mouse
os.system("unclutter -idle 0.1 -root &")

list_WebOptions = [
    # '--headless',
    '--disable-gpu',
    '--no-sandbox',
    '--lang=es',
    '--start-maximized',
    '--disable-new-menu-style',
    '--no-first-run',
    '--disable-pinch',
    '--disable-infobars',
    '--disable-translate',
    '--disable-overscroll-edge-effect',
    '--history-navigation=0',
    '--kiosk',
    '--kiosk-printing',
    '--window-size=600,400',
    '--window-position=500,200',
    '--disable-automation',
    '--disable-blink-features=AutomationControlled',
]

# path for ChromeDriver
service = Service("/usr/bin/chromedriver")
# setings Chromium
options = webdriver.ChromeOptions()

for mItem_options in list_WebOptions:
    options.add_argument(mItem_options.strip())

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# start browser
browser = webdriver.Chrome(service=service, options=options)

browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """
})

# Go to site
browser.get("http://localhost:50710")

import time
while True:
    time.sleep(10)
# close browser
browser.quit()