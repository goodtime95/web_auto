# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 09:39:14 2025

@author: Victor.Bontemps
"""

from playwright.sync_api import sync_playwright

pw = sync_playwright().start()
browser = pw.firefox.launch(
    headless=False, slow_mo=2000)
page = browser.new_page()
page.goto("http://google.com")
print(page.content())
print(page.title())
page.screenshot(path="example.png")
browser.close()