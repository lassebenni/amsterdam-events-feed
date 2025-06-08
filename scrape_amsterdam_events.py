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
        """Scrape events from I Amsterdam website"""
        logger.info("Scraping I Amsterdam events...")
        
        try:
            url = "https://www.iamsterdam.com/en/whats-on"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            events_found = 0
            
            # Look for actual event content, avoiding navigation
            event_cards = soup.find_all(['article', 'div'], class_=re.compile(r'event|listing|teaser'))
            
            # Also try to find links that look like events
            all_links = soup.find_all('a', href=True)
            
            for link in all_links[:30]:  # Check more links for events
                try:
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    
                    # Skip navigation links and look for event-like content
                    if (len(title) > 10 and 
                        not any(skip in href.lower() for skip in ['/en/', '/de/', '/fr/', '/es/', '/it/', '/pt/', '/uit', 'language']) and
                        not any(skip in title.lower() for skip in ['english', 'dutch', 'german', 'french', 'spanish', 'italian', 'português']) and
                        any(keyword in href.lower() or keyword in title.lower() 
                            for keyword in ['event', 'exhibition', 'festival', 'concert', 'show', 'museum', 'tour', 'market', 'art', 'music', 'theatre', 'comedy'])):
                        
                        full_link = urljoin(url, href)
                        
                        # Try to find parent container for more context
                        parent = link.find_parent(['article', 'div', 'section'])
                        date_text = "Check website for dates"
                        description = f"Amsterdam event: {title}"
                        
                        if parent:
                            # Look for date in parent
                            date_elem = parent.find(['time', 'span', 'div'], class_=re.compile(r'date|time'))
                            if date_elem:
                                date_text = date_elem.get_text(strip=True)
                            
                            # Look for description in parent
                            desc_elem = parent.find(['p', 'div'], class_=re.compile(r'description|summary|excerpt'))
                            if desc_elem and len(desc_elem.get_text(strip=True)) > 20:
                                description = desc_elem.get_text(strip=True)[:200] + "..."
                        
                        self.events.append({
                            'title': title,
                            'link': full_link,
                            'description': f"{date_text}\n\n{description}",
                            'source': 'I Amsterdam',
                            'date_text': date_text,
                            'pub_date': datetime.now(timezone.utc)
                        })
                        events_found += 1
                        
                        if events_found >= 15:  # Limit results
                            break
                        
                except Exception as e:
                    logger.warning(f"Error processing I Amsterdam link: {e}")
                    continue
                
                time.sleep(0.1)  # Be respectful
                
            logger.info(f"Found {events_found} events from I Amsterdam")
            
        except Exception as e:
            logger.error(f"Error scraping I Amsterdam: {e}")
    
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
        """Run all scrapers"""
        logger.info("Starting Amsterdam events scraping...")
        
        # Run all scrapers
        self.scrape_iamsterdam()
        self.scrape_timeout_amsterdam()
        self.scrape_amsterdam_nl()
        self.scrape_eventbrite_amsterdam()
        
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