#!/usr/bin/env python3
"""Fetch a URL with CloakBrowser (stealth Chromium) and print its visible text.

  python3 cfetch.py <url> [max_chars] [--html]
  CF_HEADED=1 python3 cfetch.py <url>      # headed mode for stubborn bot walls

Used during the 2026-09 research for pages that 403 plain HTTP (e.g. JobStreet
job pages). Reddit still shows a "prove your humanity" wall even headed, so use
search snippets for Reddit. The free CloakBrowser tier allows one concurrent
session: run fetches one at a time. Requires: pip install cloakbrowser
"""
import os
import re
import sys

from cloakbrowser import launch

url = sys.argv[1]
max_chars = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 40000
want_html = "--html" in sys.argv

browser = launch(headless=os.environ.get("CF_HEADED") is None, humanize=True)
try:
    page = browser.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(1500)
    if want_html:
        out = page.content()
    else:
        out = page.evaluate(
            """() => {
              ['script','style','noscript','svg','nav','footer'].forEach(
                s => document.querySelectorAll(s).forEach(e => e.remove()));
              return document.body.innerText; }"""
        )
    print(re.sub(r"\n{3,}", "\n\n", out)[:max_chars])
finally:
    browser.close()
