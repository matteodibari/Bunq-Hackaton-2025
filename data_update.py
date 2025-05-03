import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import queue

FILE_PATH = "env_variables.json"
URL = "https://doc.bunq.com"
OUTPUT_DATA_PATH = "scraped_data"

def get_change_date(file_path):

    with open(file_path, 'r') as f:
        data = json.load(f)

    change_date = data['LAST_CHANGE_DATE']
    change_date = datetime.strptime(change_date, "%Y-%m-%d %H:%M:%S")

    return data, change_date

def extract_date_from_html(url):

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for time tags
        time_tags = soup.find_all('time')
        for tag in time_tags:
            if tag.has_attr('datetime'):
                time_updated = tag['datetime']
            elif tag.text:
                time_updated = tag.text.strip()

            dt = datetime.strptime(time_updated, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
            return formatted
        
    except Exception as e:
        return f"Error: {e}"
    
def scrap_data(url, save_path):

    # Set up headless Firefox
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    
    # Base URL
    base_url = url

    # Initialize queue and set to track visited URLss
    url_queue = queue.Queue()
    visited_urls = set()

    url_queue.put(base_url)

    with open(save_path, "w", encoding="utf-8") as f:

        # Loop to crawl the pages
        while not url_queue.empty():
            current_url = url_queue.get()
            
            if current_url in visited_urls:
                continue  # Skip if already visited
            
            visited_urls.add(current_url)  # Mark as visited
            
            # Step 2: Visit the current page
            driver.get(current_url)
            time.sleep(3)  # wait for content to load
            
            # Parse the page content with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Step 3: Extract the main content of the page (adjust the selector as needed)
            main_content = soup.select_one("main")
            if main_content:
                content_text = main_content.get_text(separator="\n", strip=True)
                f.write(f"\n\n{'='*40}\n{current_url}\n{'='*40}\n")
                f.write(content_text)
            else:
                print(f" Skipped: {current_url} (no main content found)")

            # Step 4: Find all the links on the current page
            links = soup.find_all('a', href=True)

            # Step 5: Add new links to the queue (only if they haven't been visited yet)
            for link in links:
                href = link.get('href')
                if href.startswith('http') and href not in visited_urls:
                    url_queue.put(href)
                elif href.startswith('/') and base_url + href not in visited_urls:
                    url_queue.put(base_url + href)
            
            # Optional: Throttling (add a delay between requests to avoid overloading the server)
            time.sleep(1)  # Sleep for 1 second between requests to avoid hitting the server too fast

    driver.quit()

def detect_change(data, change_date, date, url, save_path):
    date_compare = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    if change_date != date_compare:
        change_date = date
        data['LAST_CHANGE_DATE'] = str(change_date)
        scrap_data(url, save_path)

    else:
        print("Already Up to date")

    return data

def main():

    data, change_date = get_change_date(FILE_PATH)

    formatted_date = extract_date_from_html(URL)

    save_path = os.path.join(OUTPUT_DATA_PATH, "bunq_full_docs.txt")

    data = detect_change(data = data, change_date= change_date, date = formatted_date, url= URL, save_path= save_path)

    with open(FILE_PATH, 'w') as f:
        # Dump the Python dictionary to JSON format in the file
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    main()