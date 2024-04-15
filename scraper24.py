
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

target = "Last RandBurg"

def clean_data_key(data):
    cleaned_data = []
    current_entry = {}

    for entry in data:
        if 'Bedrooms' in entry:  # New entry starts
            if current_entry:  # Append the previous entry if not empty
                cleaned_data.append(current_entry)
            current_entry = {}
        
        parts = entry.split('\n')
        for part in parts:
            if ':' in part:
                key, value = part.split(': ')
                current_entry[key.strip()] = value.strip()
            else:
                current_entry[part.strip()] = True
    
    # Append the last entry if not empty
    if current_entry:
        cleaned_data.append(current_entry)

    return cleaned_data
def clean_description(description):
    cleaned_description = description.replace('\n', ' ').strip()  # Replace '\n' with space and remove leading/trailing spaces
    if cleaned_description.endswith(' Read Less'):
        cleaned_description = cleaned_description[:-9].strip()  # Remove ' Read Less' from the end and strip leading/trailing spaces
    return cleaned_description
def clean_data(data):
    cleaned_data = {}
    keys = ['Province', 'City', 'Town', 'Listing Number']
    print(data)
    values = [data[i] for i in range(len(data)) if data[i] not in ['|', '>', 'Property for Sale'] and data[i] != data[i-1]]
    for key, value in zip(keys, values):
        cleaned_data[key] = value
    return cleaned_data

async def scrapeListing(page):
            
    listingData = {}
    features = []
    properties = {}

    try:
        await page.click('.js_readMoreLinkText',timeout=5000)
        
    except :
        print("Read More, button not found or clickable.")
        
    descr =  await page.locator(".js_readMoreContainer").all_inner_texts()
    size =  await page.locator(".p24_size").all_inner_texts()
    keyfeatures = await page.locator(".p24_keyFeaturesContainer").all_inner_texts()
    try:
        keyfeatures = clean_data_key(keyfeatures)[0]
        for k,v in keyfeatures.items():
            if type(keyfeatures[k]) == bool:
                features.append(k)
        
            else:
                properties[k] = v
        separator = " ; "
        features = separator.join(features)
    except :
        print("No KF")
    
    price = await page.locator(".p24_price").all_inner_texts()
    crumbs = await page.locator("#breadCrumbContainer li~ li+ li , #breadCrumbContainer li~ li+ li a").all_inner_texts()
    crumbs = clean_data(crumbs)
    element = await page.query_selector('div.js_lightboxImageWrapper.p24_galleryImageHolder.js_galleryImage.active')
    image_url = await element.get_attribute('data-image-url')
    
    listingData["features"] = features
    listingData["size"] = size[0]
    listingData["description"]= clean_description(descr[0])
    listingData["price"]= price[0]
    listingData["image"] = image_url
    listingData.update(properties)
    listingData.update(crumbs)
    df = pd.DataFrame(listingData, index=[0])
    return df

   
def press(key):
        try:
            if key == "l":
                print(key.char)
                flag = 1
            elif key =='.':
                exit()
        except :
            pass
        

async def main():
    async with async_playwright() as p:
        full_frame = pd.DataFrame()
        
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        page.set_default_timeout(31536000)

        await page.goto("https://www.property24.com/")
        flag = True
        while flag:
            scrape = input("Scrap Listing?")
            if scrape == "1":
                df = await scrapeListing(page)
                full_frame = pd.concat([full_frame,df],axis=0,ignore_index=True)
                full_frame.to_csv(f"C:/Users/Omniscience is Dead/Desktop/pwp24/csvs/{target}.csv",sep=',', encoding='utf-8')   
                print(full_frame) 
            if scrape == ".":
                print("Bye Bye!")
                flag=False
                await browser.close()
                           
                
                

    

asyncio.run(main())