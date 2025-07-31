#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

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
]

# path for ChromeDriver
service = Service("/usr/bin/chromedriver")
# setings Chromium
options = webdriver.ChromeOptions()

for mItem_options in list_WebOptions:
    options.add_argument(mItem_options.strip())

# start browser
browser = webdriver.Chrome(service=service, options=options)
# Go to site
browser.get("http://localhost:50710")

time.sleep(10)
# close browser
browser.quit()
