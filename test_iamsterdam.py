#!/usr/bin/env python3
"""
Test script to debug I amsterdam scraping
"""
import requests
from bs4 import BeautifulSoup
import re

def test_iamsterdam_scraping():
    """Test scraping I amsterdam agenda"""
    print("Testing I amsterdam agenda scraping...")
    
    try:
        url = "https://www.iamsterdam.com/uit/agenda"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Successfully fetched page (status: {response.status_code})")
        print(f"Content length: {len(response.text)} characters")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Print first 2000 characters to see structure
        print("\n=== FIRST 2000 CHARACTERS ===")
        print(response.text[:2000])
        
        # Look for common event-related patterns
        print("\n=== SEARCHING FOR EVENTS ===")
        
        # Search for date patterns
        date_pattern = r'(\d{1,2})(jan|feb|mrt|apr|mei|jun|jul|aug|sep|okt|nov|dec)\s*\'(\d{2})'
        date_matches = re.findall(date_pattern, response.text.lower())
        print(f"Found {len(date_matches)} date matches: {date_matches[:5]}")
        
        # Look for links
        links = soup.find_all('a', href=True)
        print(f"Found {len(links)} total links")
        
        # Look for event-like text
        event_keywords = ['amsterdam 750', 'tentoonstelling', 'concert', 'festival', 'museum', 'expositie']
        for keyword in event_keywords:
            if keyword in response.text.lower():
                print(f"✅ Found keyword: {keyword}")
            else:
                print(f"❌ Missing keyword: {keyword}")
        
        # Look for structured content
        divs = soup.find_all('div')
        print(f"Found {len(divs)} div elements")
        
        # Check if page has proper content or is redirected/blocked
        if len(response.text) < 10000:
            print("⚠️  Warning: Page content seems too short, might be blocked or redirected")
        
        # Look for any text that contains "agenda" or "event"
        page_text = soup.get_text().lower()
        if 'agenda' in page_text:
            print("✅ Found 'agenda' in page text")
        if 'event' in page_text:
            print("✅ Found 'event' in page text")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_iamsterdam_scraping() 