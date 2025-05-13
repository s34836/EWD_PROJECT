import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
from datetime import datetime

def load_progress():
    try:
        if os.path.exists('scraper_progress.json'):
            with open('scraper_progress.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading progress file: {e}")
    return {'last_page': 0, 'total_urls': 0, 'last_updated': None}

def save_progress(progress_data):
    try:
        progress_data['last_updated'] = datetime.now().isoformat()
        with open('scraper_progress.json', 'w') as f:
            json.dump(progress_data, f, indent=2)
    except Exception as e:
        print(f"Error saving progress file: {e}")

def append_urls_to_file(urls, filename):
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            for url in urls:
                f.write(f"{url}\n")
        return True
    except Exception as e:
        print(f"Error appending URLs to file: {e}")
        return False

def get_otodom_listings(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            elif response.status_code == 429:  # Too Many Requests
                wait_time = retry_delay * (attempt + 1)
                print(f"Rate limited. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"Failed to retrieve the page. Status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return None
    return None

def extract_urls(soup):
    if not soup:
        return []
    
    urls = []
    try:
        listing_containers = soup.select('article.css-136g1q2')
        
        for container in listing_containers:
            try:
                url_element = container.select_one('a[href*="/pl/oferta/"]')
                if url_element and 'href' in url_element.attrs:
                    url = url_element['href']
                    if not url.startswith('http'):
                        url = "https://www.otodom.pl" + url
                    urls.append(url)
            except Exception as e:
                print(f"Error extracting URL from container: {e}")
                continue
    except Exception as e:
        print(f"Error processing page content: {e}")
    
    return urls

def scrape_multiple_pages(base_url, num_pages=200):
    progress = load_progress()
    start_page = progress['last_page'] + 1
    total_urls = progress['total_urls']
    
    if start_page > num_pages:
        print(f"All pages already processed (up to page {num_pages})")
        return total_urls
    
    print(f"Resuming from page {start_page}")
    
    for page in range(start_page, num_pages + 1):
        try:
            page_url = f"{base_url}&page={page}"
            print(f"Scraping page {page}: {page_url}")
            
            soup = get_otodom_listings(page_url)
            if soup:
                urls = extract_urls(soup)
                if urls:
                    if append_urls_to_file(urls, 'warsaw_rental_urls.txt'):
                        total_urls += len(urls)
                        progress['last_page'] = page
                        progress['total_urls'] = total_urls
                        save_progress(progress)
                        print(f"Found and saved {len(urls)} URLs from page {page}")
                    else:
                        print(f"Failed to save URLs from page {page}")
                else:
                    print(f"No URLs found on page {page}")
            
            # Be respectful with rate limiting
            time.sleep(random.uniform(2, 5))
            
        except Exception as e:
            print(f"Error processing page {page}: {e}")
            # Save progress before exiting
            save_progress(progress)
            raise
    
    return total_urls

def main():
    try:
        base_url = "https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/mazowieckie/warszawa/warszawa/warszawa?ownerTypeSingleSelect=ALL&viewType=listing"
        
        # Create or clear the output file if starting from page 1
        progress = load_progress()
        if progress['last_page'] == 0:
            open('warsaw_rental_urls.txt', 'w').close()
        
        # Scrape URLs
        total_urls = scrape_multiple_pages(base_url, num_pages=200)
        
        print(f"\nScraping completed. Total URLs collected: {total_urls}")
        print("Results saved to warsaw_rental_urls.txt")
        print("Progress saved to scraper_progress.json")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        progress = load_progress()
        print(f"Progress saved: {progress['total_urls']} URLs collected up to page {progress['last_page']}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        progress = load_progress()
        print(f"Progress saved: {progress['total_urls']} URLs collected up to page {progress['last_page']}")

if __name__ == "__main__":
    main()