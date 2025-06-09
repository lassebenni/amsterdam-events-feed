#!/usr/bin/env python3
"""
Amsterdam Events Scraper
Collects event data from multiple Amsterdam sources and generates an RSS feed.
"""

import requests
import time
import json
import re
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin, urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AmsterdamEventsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AmsterdamEventsBot/1.0 (Educational Purpose)'
        })
        self.events = []
        
    def scrape_iamsterdam(self):
        """Scrape events from I Amsterdam website - official Amsterdam events agenda"""
        logger.info("Scraping I Amsterdam events agenda...")
        
        try:
            url = "https://www.iamsterdam.com/uit/agenda"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            events_found = 0
            
            logger.info("Looking for Amsterdam events in page content...")
            
            # Strategy 1: Look for links that contain event keywords and seem to be events
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                try:
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    
                    # Skip navigation and empty links
                    if not title or len(title) < 10 or not href:
                        continue
                    
                    # Look for event-related keywords in title
                    event_keywords = [
                        'amsterdam 750', 'tentoonstelling', 'concert', 'festival', 
                        'museum', 'expositie', 'show', 'wandeling', 'tour', 'kunst', 
                        'theater', 'muziek', 'evenement', 'activiteit', 'bezienswaardigheid'
                    ]
                    
                    # Skip common navigation terms
                    skip_terms = [
                        'nederlands', 'english', 'deutsch', 'français', 'español',
                        'cookies', 'privacy', 'contact', 'volg ons', 'over ons',
                        'taal', 'language', 'filter', 'sorteren', 'ontdek amsterdam',
                        'i amsterdam store', 'city card'
                    ]
                    
                    if any(skip in title.lower() for skip in skip_terms):
                        continue
                    
                    # Check if this looks like an event
                    is_event = any(keyword in title.lower() for keyword in event_keywords)
                    
                    # Also check if href looks event-related
                    if not is_event and href:
                        is_event = any(keyword in href.lower() for keyword in 
                                     ['event', 'agenda', 'activit', 'museum', 'festival', 'concert'])
                    
                    if is_event:
                        full_link = urljoin(url, href)
                        
                        # Try to find additional context from parent elements
                        parent = link.find_parent(['div', 'article', 'section', 'li'])
                        description = f"Discover this Amsterdam event: {title}"
                        date_info = "Check website for dates and times"
                        location = ""
                        
                        if parent:
                            parent_text = parent.get_text()
                            
                            # Look for date patterns in parent context
                            # Pattern for dates like "04 jun '25" or "4 juni 2025"
                            date_patterns = [
                                r'(\d{1,2})\s*(jan|feb|mar|apr|mei|jun|jul|aug|sep|okt|nov|dec)[a-z]*\s*\W?(\d{2,4})',
                                r'(\d{1,2})-(\d{1,2})-(\d{4})',
                                r'(\d{4})-(\d{1,2})-(\d{1,2})'
                            ]
                            
                            for pattern in date_patterns:
                                date_matches = re.findall(pattern, parent_text.lower())
                                if date_matches:
                                    match = date_matches[0]
                                    if len(match) >= 3:
                                        try:
                                            day, month, year = match
                                            # Convert Dutch months
                                            month_map = {
                                                'jan': 'January', 'feb': 'February', 'mar': 'March', 'mrt': 'March',
                                                'apr': 'April', 'mei': 'May', 'jun': 'June',
                                                'jul': 'July', 'aug': 'August', 'sep': 'September',
                                                'okt': 'October', 'nov': 'November', 'dec': 'December'
                                            }
                                            if month in month_map:
                                                date_info = f"{day} {month_map[month]} {year if len(year) == 4 else '20' + year}"
                                                break
                                        except:
                                            continue
                            
                            # Look for location indicators
                            location_indicators = ['amsterdam', 'museum', 'theater', 'concertgebouw', 'vondelpark', 'centrum']
                            for indicator in location_indicators:
                                if indicator in parent_text.lower() and indicator not in title.lower():
                                    location = indicator.title()
                                    break
                        
                        description = f"Official Amsterdam event from I amsterdam agenda.\n\nDate: {date_info}"
                        if location:
                            description += f"\nLocation: {location}"
                        description += f"\n\nSource: I amsterdam ({url})"
                        
                        self.events.append({
                            'title': title,
                            'link': full_link,
                            'description': description,
                            'source': 'I Amsterdam Official',
                            'date_text': date_info,
                            'pub_date': datetime.now(timezone.utc)
                        })
                        events_found += 1
                        
                        if events_found >= 15:  # Reasonable limit
                            break
                            
                except Exception as e:
                    logger.warning(f"Error processing I Amsterdam link: {e}")
                    continue
                
                time.sleep(0.1)  # Be respectful
            
            # Strategy 2: If we didn't find many events, look for any structured content with keywords
            if events_found < 5:
                logger.info("Trying alternative content extraction...")
                
                # Look for text that contains Amsterdam 750 events (current special events)
                amsterdam_750_content = soup.find_all(text=re.compile(r'amsterdam\s*750', re.I))
                
                for content in amsterdam_750_content[:10]:
                    try:
                        parent = content.parent if hasattr(content, 'parent') else None
                        if parent:
                            # Try to find the full event text
                            event_text = parent.get_text(strip=True)
                            if len(event_text) > 20 and len(event_text) < 200:
                                # Look for associated link
                                link_elem = parent.find('a', href=True)
                                event_link = urljoin(url, link_elem['href']) if link_elem else url
                                
                                self.events.append({
                                    'title': f"Amsterdam 750: {event_text[:100]}",
                                    'link': event_link,
                                    'description': f"Special Amsterdam 750 anniversary event.\n\n{event_text}\n\nSource: I amsterdam ({url})",
                                    'source': 'I Amsterdam Official',
                                    'date_text': 'Part of Amsterdam 750 celebrations',
                                    'pub_date': datetime.now(timezone.utc)
                                })
                                events_found += 1
                                
                                if events_found >= 10:
                                    break
                    except Exception as e:
                        logger.warning(f"Error processing Amsterdam 750 content: {e}")
                        continue
                
            logger.info(f"Found {events_found} events from I Amsterdam agenda")
            
        except Exception as e:
            logger.error(f"Error scraping I Amsterdam agenda: {e}")
    
    def scrape_timeout_amsterdam(self):
        """Scrape events from Time Out Amsterdam"""
        logger.info("Scraping Time Out Amsterdam events...")
        
        try:
            url = "https://www.timeout.com/amsterdam/things-to-do"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            events_found = 0
            
            # Look for event listings
            event_items = soup.find_all(['div', 'article'], class_=re.compile(r'event|listing|card'))
            
            for item in event_items[:15]:  # Limit results
                try:
                    # Extract title
                    title_elem = item.find(['h1', 'h2', 'h3'], class_=re.compile(r'title|heading'))
                    if not title_elem:
                        title_elem = item.find('a')
                    
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    
                    # Extract link
                    link_elem = item.find('a', href=True)
                    if link_elem:
                        link = urljoin(url, link_elem['href'])
                    else:
                        continue
                    
                    # Extract description
                    desc_elem = item.find(['p', 'div'], class_=re.compile(r'description|excerpt'))
                    description = desc_elem.get_text(strip=True) if desc_elem else f"Time Out Amsterdam: {title}"
                    
                    if title and link and len(title) > 5:  # Basic validation
                        self.events.append({
                            'title': title,
                            'link': link,
                            'description': description,
                            'source': 'Time Out Amsterdam',
                            'date_text': "Check website for dates",
                            'pub_date': datetime.now(timezone.utc)
                        })
                        events_found += 1
                        
                except Exception as e:
                    logger.warning(f"Error processing Time Out event: {e}")
                    continue
                    
                time.sleep(0.3)  # Be respectful
                
            logger.info(f"Found {events_found} events from Time Out Amsterdam")
            
        except Exception as e:
            logger.error(f"Error scraping Time Out Amsterdam: {e}")
    
    def scrape_amsterdam_nl(self):
        """Scrape events from Amsterdam.nl"""
        logger.info("Scraping Amsterdam.nl events...")
        
        try:
            url = "https://www.amsterdam.nl/en/"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            events_found = 0
            
            # Look for event or activity links
            links = soup.find_all('a', href=True)
            
            for link in links[:10]:  # Limit to prevent spam
                try:
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    
                    # Filter for event-like content
                    if (len(title) > 10 and 
                        any(keyword in title.lower() for keyword in ['event', 'festival', 'show', 'concert', 'exhibition', 'museum', 'tour', 'market']) and
                        href and not href.startswith('#')):
                        
                        full_link = urljoin(url, href)
                        
                        self.events.append({
                            'title': f"Amsterdam Activity: {title}",
                            'link': full_link,
                            'description': f"Discover this activity in Amsterdam: {title}",
                            'source': 'Amsterdam.nl',
                            'date_text': "Ongoing",
                            'pub_date': datetime.now(timezone.utc)
                        })
                        events_found += 1
                        
                except Exception as e:
                    logger.warning(f"Error processing Amsterdam.nl link: {e}")
                    continue
                    
                time.sleep(0.1)
                
            logger.info(f"Found {events_found} activities from Amsterdam.nl")
            
        except Exception as e:
            logger.error(f"Error scraping Amsterdam.nl: {e}")
    
    def deduplicate_events(self):
        """Remove duplicate events based on title similarity"""
        logger.info("Removing duplicate events...")
        
        unique_events = []
        seen_titles = set()
        
        for event in self.events:
            # Create a normalized title for comparison
            normalized_title = re.sub(r'[^a-zA-Z0-9\s]', '', event['title'].lower()).strip()
            
            if normalized_title not in seen_titles and len(normalized_title) > 5:
                seen_titles.add(normalized_title)
                unique_events.append(event)
        
        original_count = len(self.events)
        self.events = unique_events
        logger.info(f"Removed {original_count - len(self.events)} duplicate events")
    
    def generate_rss_feed(self, output_file='events.xml'):
        """Generate RSS feed from collected events"""
        logger.info(f"Generating RSS feed with {len(self.events)} events...")
        
        fg = FeedGenerator()
        fg.title('Amsterdam Events Feed')
        fg.link(href='https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml')
        fg.description('Curated upcoming events and activities in Amsterdam')
        fg.language('en')
        fg.lastBuildDate(datetime.now(timezone.utc))
        fg.generator('Amsterdam Events Scraper v1.0')
        
        # Add each event as a feed entry
        for event in self.events:
            fe = fg.add_entry()
            fe.title(event['title'])
            fe.link(href=event['link'])
            fe.description(f"Source: {event['source']}\n\n{event['description']}")
            fe.pubDate(event['pub_date'])
            fe.guid(event['link'])
        
        # Generate the RSS XML
        fg.rss_file(output_file)
        logger.info(f"RSS feed saved to {output_file}")
    
    def save_events_json(self, output_file='events.json'):
        """Save events as JSON for debugging/alternative use"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, indent=2, default=str, ensure_ascii=False)
        logger.info(f"Events data saved to {output_file}")
    
    def scrape_eventbrite_amsterdam(self):
        """Scrape public events from Eventbrite in Amsterdam"""
        logger.info("Scraping Eventbrite Amsterdam events...")
        
        try:
            # Eventbrite's public search for Amsterdam events
            url = "https://www.eventbrite.com/d/netherlands--amsterdam/events/"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            events_found = 0
            
            # Look for event cards
            event_cards = soup.find_all(['div', 'article'], 
                                       attrs={'data-event-id': True})  # Eventbrite uses data-event-id
            
            if not event_cards:
                # Fallback: look for links containing "events"
                event_links = soup.find_all('a', href=re.compile(r'/e/'))
                
                for link in event_links[:10]:
                    try:
                        title = link.get_text(strip=True)
                        href = link.get('href', '')
                        
                        if len(title) > 10 and not any(skip in title.lower() for skip in ['sign up', 'log in', 'create']):
                            full_link = urljoin(url, href)
                            
                            self.events.append({
                                'title': f"Eventbrite: {title}",
                                'link': full_link,
                                'description': f"Find this event on Eventbrite: {title}",
                                'source': 'Eventbrite Amsterdam',
                                'date_text': "Check Eventbrite for dates",
                                'pub_date': datetime.now(timezone.utc)
                            })
                            events_found += 1
                            
                            if events_found >= 5:  # Limit Eventbrite results
                                break
                                
                    except Exception as e:
                        logger.warning(f"Error processing Eventbrite link: {e}")
                        continue
                        
                    time.sleep(0.2)
            
            logger.info(f"Found {events_found} events from Eventbrite Amsterdam")
            
        except Exception as e:
            logger.error(f"Error scraping Eventbrite Amsterdam: {e}")
    
    def scrape_all(self):
        """Run all scrapers - prioritizing official I amsterdam source for current month events"""
        logger.info("Starting Amsterdam events scraping...")
        
        # Prioritize official I amsterdam agenda for current month events
        self.scrape_iamsterdam()
        
        # Only scrape additional sources if we don't have enough events from official source
        if len(self.events) < 10:
            logger.info("Adding events from additional sources...")
            self.scrape_eventbrite_amsterdam()
            self.scrape_timeout_amsterdam()
            self.scrape_amsterdam_nl()
        
        # Clean up the data
        self.deduplicate_events()
        
        logger.info(f"Scraping complete. Total events collected: {len(self.events)}")
        
        return self.events

def main():
    """Main execution function"""
    scraper = AmsterdamEventsScraper()
    
    # Scrape all sources
    events = scraper.scrape_all()
    
    if events:
        # Generate RSS feed
        scraper.generate_rss_feed()
        
        # Save JSON for debugging
        scraper.save_events_json()
        
        print(f"✅ Successfully generated feed with {len(events)} events")
        print("📄 Files created: events.xml, events.json")
        print("🔗 Ready to use with WordPress RSS plugins!")
    else:
        print("❌ No events found. Check the scrapers.")

if __name__ == "__main__":
    main() 