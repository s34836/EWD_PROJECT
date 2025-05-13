import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import json
import os
from datetime import datetime

# Constants
PROGRESS_FILE = 'scraping_progress.json'
OUTPUT_FILE = 'warsaw_rentals.txt'

def load_progress():
    """Load progress from JSON file or create new if doesn't exist"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error reading progress file. Starting from beginning.")
            return {'last_processed': -1, 'start_time': datetime.now().isoformat()}
    return {'last_processed': -1, 'start_time': datetime.now().isoformat()}

def save_progress(last_processed):
    """Save current progress to JSON file"""
    progress_data = {
        'last_processed': last_processed,
        'start_time': datetime.now().isoformat()
    }
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress_data, f)
    except Exception as e:
        print(f"Error saving progress: {str(e)}")

def load_or_create_dataframe(urls):
    """Load existing CSV or create new DataFrame with URLs"""
    if os.path.exists(OUTPUT_FILE):
        try:
            existing_df = pd.read_csv(OUTPUT_FILE)
            # If we have existing data, merge with new URLs
            new_urls = set(urls) - set(existing_df['url'])
            if new_urls:
                new_df = pd.DataFrame({'url': list(new_urls)})
                new_df['raw_json'] = None
                return pd.concat([existing_df, new_df], ignore_index=True)
            return existing_df
        except Exception as e:
            print(f"Error reading existing CSV: {str(e)}")
            return create_new_dataframe(urls)
    return create_new_dataframe(urls)

def create_new_dataframe(urls):
    """Create new DataFrame with required columns and URLs"""
    df = pd.DataFrame({'url': urls})
    df['raw_json'] = None
    return df

def save_processed_url(df, idx):
    """Save a single processed URL to CSV"""
    try:
        # Create a DataFrame with just the processed row
        processed_df = pd.DataFrame([df.iloc[idx]])
        
        if os.path.exists(OUTPUT_FILE):
            # Append to existing file without header
            processed_df.to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
        else:
            # Create new file with header
            processed_df.to_csv(OUTPUT_FILE, index=False)
            
        print(f"Saved URL {idx + 1} to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving processed URL: {str(e)}")

def extract_json_data(html_content):
    """Extract JSON data from HTML content"""
    try:
        # Look for the script tag containing the JSON data with the exact format
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json" crossorigin="anonymous">(.*?)</script>'
        match = re.search(json_pattern, html_content, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            # Parse the JSON string
            json_data = json.loads(json_str)
            return json_data
        return None
    except Exception as e:
        print(f"Error extracting JSON data: {str(e)}")
        return None

def extract_details_from_json(json_data):
    """Extract relevant details from the JSON data"""
    try:
        if not json_data:
            return None

        # Navigate through the JSON structure to find the property details
        property_data = json_data.get('props', {}).get('pageProps', {}).get('ad', {})
        
        if not property_data:
            return None

        return {
            'raw_json': json.dumps(property_data)  # Store the complete property data
        }
    except Exception as e:
        print(f"Error extracting details from JSON: {str(e)}")
        return None

# Read URLs from the text file
try:
    with open('warsaw_rental_urls.txt', 'r') as file:
        urls = file.readlines()
except Exception as e:
    print(f"Error reading URLs file: {str(e)}")
    exit(1)

# Clean URLs (remove whitespace and newlines)
urls = [url.strip() for url in urls if url.strip()]  # Only keep non-empty URLs

if not urls:
    print("No URLs found in the file!")
    exit(1)

print(f"Loaded {len(urls)} URLs from file")

# Function to scrape rental details
def scrape_rental_details(url):
    try:
        # Add headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Extract JSON data from the page
        json_data = extract_json_data(response.text)
        
        if json_data:
            # Extract details from the JSON data
            details = extract_details_from_json(json_data)
            if details:
                return details
        
        return {'raw_json': None}
    
    except requests.Timeout:
        print(f"Timeout while scraping {url}")
        return None
    except requests.RequestException as e:
        print(f"Request error while scraping {url}: {str(e)}")
        return None
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

# Load progress and existing data
progress = load_progress()
df = load_or_create_dataframe(urls)

# Get the starting index
start_idx = progress['last_processed'] + 1
if start_idx >= len(df):
    print("All URLs have been processed!")
    exit(0)

print(f"Starting from URL {start_idx + 1} of {len(df)}")

# Scrape details for each URL
try:
    for idx in range(start_idx, len(df)):
        print(f"Scraping URL {idx + 1}/{len(df)}")
        details = scrape_rental_details(df.iloc[idx]['url'])
        
        if details:
            df.at[idx, 'raw_json'] = details['raw_json']
            
            # Save the processed URL immediately
            save_processed_url(df, idx)
        
        # Update progress after each URL
        save_progress(idx)
        
        time.sleep(1)  # Add delay between requests to be polite

except KeyboardInterrupt:
    print("\nScraping interrupted by user!")
    save_progress(idx - 1)
    exit(0)
except Exception as e:
    print(f"\nUnexpected error: {str(e)}")
    save_progress(idx - 1)
    exit(1)

# Final progress update
save_progress(len(df) - 1)

# Display the results
print("\nScraping completed!")
print(f"Total unique URLs processed: {len(df)}")
print("\nFirst few entries:")
print(df.head())
