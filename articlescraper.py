import asyncio
import hashlib
import time
import random
import numpy as np
import pandas as pd

import os
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from pynput.keyboard import *

target="Buying Advice"

async def scrapeArticle(page):
    title = await page.locator("h1").all_inner_texts()
    article =  await page.locator(".article div").all_inner_texts()
    return pd.DataFrame({"Title":title,"Article":article})

async def get_article_links(page):
  # Improved selector targeting class and title attribute
  hrefs = await page.evaluate('''() => {
                    const anchors = Array.from(document.querySelectorAll('a.title'));
                    return anchors.map(anchor => anchor.href);}''')
 
  
  return hrefs


async def main():
    async with async_playwright() as p:
        full_frame = pd.DataFrame()
        flag = True
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        page.set_default_timeout(31536000)
        await page.goto("https://www.privateproperty.co.za/advice/property/buying-advice/3351")
        
        pagelinks = [f"https://www.privateproperty.co.za/advice/property/buying-advice/3351?page={pagenav}" for pagenav in range(1,249)]
        
        for pagelink in pagelinks :
            await page.goto(pagelink)
            time.sleep(2)
            links = await get_article_links(page)
            for link in links:
                await page.goto(link)
                time.sleep(1)
                df = await scrapeArticle(page)
                full_frame = pd.concat([full_frame,df],axis=0,ignore_index=True)
                full_frame.to_csv(f"C:/Users/Omniscience is Dead/Desktop/pwp24/articles/{target}.csv",sep=',', encoding='utf-8')   
                print(full_frame)
                time.sleep(1)
                await page.go_back()
                time.sleep(5)
            time.sleep(random.randint(60,60*5))
            
                
                

    await browser.close()

asyncio.run(main())