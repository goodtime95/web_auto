# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 09:39:14 2025

@author: Victor.Bontemps
"""

from playwright.sync_api import sync_playwright
from urllib.request import urlretrieve

pw = sync_playwright().start()
browser = pw.firefox.launch(
    headless=False 
    ,slow_mo=2000
    )
page = browser.new_page()
page.goto("https://arxiv.org/search")
page.get_by_placeholder("Search term...").fill(
    "structured products"
    )
page.get_by_role("button").get_by_text(
    "Search"
    ).nth(1).click()
links = page.locator(
    "xpath=//a[contains(@href, 'arxiv.org/pdf')]"
             ).all()
for link in links:
    url = link.get_attribute("href")
    urlretrieve(url, "data/" + url[-5:] + ".pdf" )
page.screenshot(path="example.png")
browser.close()