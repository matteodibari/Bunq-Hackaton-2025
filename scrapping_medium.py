"""
This script scrapes articles from the Medium blog of bunq developers corner.
It extracts article links, content, and saves them to text files.
"""

import requests
from bs4 import BeautifulSoup
import time
import os
import re

class MediumScraper:
    def __init__(self, url):
        self.base_url = url
        self.article_links = []
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.output_dir = 'bunq_blog_articles'
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def get_soup(self, url):
        """Get BeautifulSoup object for a given URL"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_article_links(self):
        """Extract all article links from the main blog page"""
        soup = self.get_soup(self.base_url)
        if not soup:
            return
        
        # Find all article links (this might need adjusting based on Medium's structure)
        articles = soup.find_all('article')
        for article in articles:
            link_element = article.find('a', href=True)
            if link_element:
                link = link_element['href']
                # Make sure the link is an absolute URL
                if not link.startswith('http'):
                    if link.startswith('/'):
                        link = 'https://medium.com' + link
                    else:
                        link = 'https://medium.com/' + link
                
                self.article_links.append(link)
                print(f"Found article: {link}")
        
        # Alternative way to find articles if the above doesn't work
        if not self.article_links:
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                # Check if it's a Medium article link
                if '/bunq-developers-corner/' in href and not href.endswith('/bunq-developers-corner'):
                    if not href.startswith('http'):
                        href = 'https://medium.com' + href
                    self.article_links.append(href)
                    print(f"Found article: {href}")
    
    def clean_text(self, text):
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove empty lines
        text = re.sub(r'^\s*$', '', text, flags=re.MULTILINE)
        return text.strip()
    
    def extract_article_content(self, url):
        """Extract content from a single article"""
        soup = self.get_soup(url)
        if not soup:
            return None
        
        # Extract title
        title_element = soup.find('h1')
        title = title_element.text if title_element else "Untitled Article"
        
        # Extract article sections
        article_content = []
        
        # Extract main article content
        article_element = soup.find('article')
        if article_element:
            # Get all paragraphs
            paragraphs = article_element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'code', 'blockquote'])
            for p in paragraphs:
                article_content.append(p.text.strip())
        
        # If we couldn't find article content, try a more generic approach
        if not article_content:
            # Extract all paragraphs from the page
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for p in paragraphs:
                if len(p.text.strip()) > 40:  # Only include substantial paragraphs
                    article_content.append(p.text.strip())
        
        # Combine all content
        full_content = f"TITLE: {title}\nURL: {url}\n\n" + "\n\n".join(article_content)
        return self.clean_text(full_content)
    
    def save_article(self, article_content, url):
        """Save article content to a text file"""
        # Create a safe filename from the URL
        filename = url.split('/')[-1]
        if not filename:
            filename = 'article'
        filename = re.sub(r'[^\w\-]', '_', filename)
        filename = f"{filename}.txt"
        
        # Save to file
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(article_content)
        
        return filepath
    
    def save_all_links(self):
        """Save all article links to a text file"""
        with open(os.path.join(self.output_dir, 'all_links.txt'), 'w', encoding='utf-8') as f:
            for link in self.article_links:
                f.write(f"{link}\n")
    
    def save_combined_content(self, contents):
        """Save all article contents to a single file"""
        with open(os.path.join(self.output_dir, 'all_articles.txt'), 'w', encoding='utf-8') as f:
            f.write("\n\n" + "="*50 + "\n\n".join(contents))
    
    def scrape(self):
        """Main scraping function"""
        print(f"Starting to scrape {self.base_url}")
        
        # Extract all article links
        self.extract_article_links()
        print(f"Found {len(self.article_links)} articles")
        
        # Save all links
        self.save_all_links()
        
        # Extract content from each article
        all_contents = []
        for i, link in enumerate(self.article_links):
            print(f"Scraping article {i+1}/{len(self.article_links)}: {link}")
            
            # Add delay to avoid being blocked
            if i > 0:
                time.sleep(2)
            
            content = self.extract_article_content(link)
            if content:
                filepath = self.save_article(content, link)
                all_contents.append(content)
                print(f"Saved to {filepath}")
            else:
                print(f"Failed to extract content from {link}")
        
        # Save all content to a single file
        self.save_combined_content(all_contents)
        print(f"Scraping completed. All articles saved to {self.output_dir}")


# Run the scraper
if __name__ == "__main__":
    scraper = MediumScraper("https://medium.com/bunq-developers-corner")
    scraper.scrape()