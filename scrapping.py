from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import queue

# Set up headless Firefox
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

# Base URL
base_url = "https://doc.bunq.com"

# Initialize queue and set to track visited URLs
url_queue = queue.Queue()
visited_urls = set()

# Step 1: Add the initial URL to the queue
url_queue.put(base_url)

# Prepare file to store scraped content
with open("bunq_full_docs.txt", "w", encoding="utf-8") as f:

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

print("All pages scraped and saved to bunq_full_docs.txt")
driver.quit()
