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
import asyncio
from playwright.async_api import async_playwright
import translators as ts

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AmsterdamEventsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        self.events = []

    async def extract_event_image_playwright(self, page, event_url):
        """Extract the main image from an event page using Playwright"""
        try:
            logger.info(f"Extracting image from: {event_url}")
            await page.goto(event_url, wait_until='domcontentloaded')
            
            # Try multiple selectors for finding images
            image_selectors = [
                'meta[property="og:image"]',
                'img[src*="thefeedfactory"]',
                'article img[src]',
                'main img[src]'
            ]
            
            for selector in image_selectors:
                element = await page.query_selector(selector)
                if element:
                    if selector.startswith('meta'):
                        image_url = await element.get_attribute('content')
                    else:
                        image_url = await element.get_attribute('src')

                    if image_url:
                        # Convert relative URLs to absolute
                        if image_url.startswith('/'):
                            image_url = urljoin(page.url, image_url)
                        
                        logger.info(f"Found image: {image_url}")
                        return image_url
            
            logger.warning(f"No suitable image found for {event_url}")
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting image from {event_url}: {e}")
            return None

    async def scrape_iamsterdam_playwright(self):
        """Scrape events from I Amsterdam using Playwright to handle dynamic content"""
        logger.info("Scraping I Amsterdam events agenda with Playwright...")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context()
                page = await context.new_page()
                
                await page.goto("https://www.iamsterdam.com/uit/agenda", wait_until='networkidle')
                
                logger.info("Page loaded. Finding event links...")
                
                # Use Playwright to find all event links and extract hrefs immediately
                link_handles = await page.query_selector_all('a[href*="/uit/agenda/"]')
                event_urls = []
                for link_handle in link_handles:
                    href = await link_handle.get_attribute('href')
                    if href:
                        # Filter out category pages by checking URL path depth.
                        parsed_url = urlparse(href)
                        if len(parsed_url.path.split('/')) >= 5:
                            event_urls.append(urljoin("https://www.iamsterdam.com", href))

                await browser.close() # Close the browser now that we have the URLs

                if not event_urls:
                    logger.warning("No valid event URLs found on the page.")
                    return
                
                logger.info(f"Found {len(event_urls)} potential event URLs. Processing them now...")

                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    context = await browser.new_context()

                    for url in event_urls:
                        try:
                            page = await context.new_page()
                            await page.goto(url, wait_until='domcontentloaded')

                            title = await page.title()
                            
                            # Try to find a more specific title within the page
                            h1_title = await page.query_selector('h1')
                            if h1_title:
                                title = await h1_title.text_content()
                            
                            description = ""
                            meta_desc = await page.query_selector('meta[name="description"]')
                            if meta_desc:
                                description = await meta_desc.get_attribute('content')

                            if not description:
                                main_content = await page.query_selector('main')
                                if main_content:
                                    description = await main_content.text_content()

                            description = description.strip().replace('\n', ' ')[:500]

                            # Translate description to English
                            try:
                                if description:
                                    # Using Google translator
                                    translated_description = ts.translate_text(description, translator='google', to_language='en')
                                    description = translated_description
                                    logger.info(f"Successfully translated description for: {title}")
                            except Exception as e:
                                logger.warning(f"Could not translate description for {title}: {e}")

                            event_image = await self.extract_event_image_playwright(page, url)
                            
                            event_data = {
                                "title": title.strip(),
                                "link": url,
                                "description": description,
                                "source": "I Amsterdam Official",
                                "date_text": "Check website for dates",
                                "pub_date": datetime.now(timezone.utc),
                                "tags": [],
                                "location": "Amsterdam",
                                "image": event_image if event_image else None
                            }

                            if not any(e['link'] == event_data['link'] for e in self.events):
                                self.events.append(event_data)
                            
                            await page.close()

                        except Exception as e:
                            logger.warning(f"Error processing page {url}: {e}")
                            if 'page' in locals() and not page.is_closed():
                                await page.close()
                            continue
                    
                    await browser.close()

                logger.info(f"Finished processing. Found {len(self.events)} unique events.")

        except Exception as e:
            logger.error(f"Error scraping I Amsterdam agenda with Playwright: {e}")

    def scrape_iamsterdam(self):
        """Scrape events from I Amsterdam website - official Amsterdam events agenda with images"""
        asyncio.run(self.scrape_iamsterdam_playwright())

    def deduplicate_events(self):
        """Remove duplicate events based on title similarity"""
        logger.info("Removing duplicate events...")

        unique_events = []
        seen_titles = set()

        for event in self.events:
            # Create a normalized title for comparison
            normalized_title = re.sub(
                r"[^a-zA-Z0-9\s]", "", event["title"].lower()
            ).strip()

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
        fg.description('Curated upcoming events and activities in Amsterdam from I amsterdam official agenda')
        fg.language('en')
        fg.lastBuildDate(datetime.now(timezone.utc))
        fg.generator('Amsterdam Events Scraper v10.0')
        
        # Add each event as a feed entry
        for event in self.events:
            fe = fg.add_entry()
            fe.id(event['link'])
            fe.title(event['title'])
            fe.link(href=event['link'])
            fe.pubDate(datetime.now(timezone.utc))
            
            # Create well-structured HTML content for better WordPress display
            content_parts = []
            
            # Event header with structured information
            content_parts.append('<div class="amsterdam-event-card">')
            
            # Event details section with clean structure
            content_parts.append('<div class="event-details">')
            
            # Date information
            content_parts.append('<div class="event-info-line">')
            content_parts.append('<span class="event-icon">📅</span>')
            content_parts.append('<span class="event-label">Date:</span>')
            content_parts.append(f'<span class="event-value">{event.get("date_text", "Check website for specific dates and times")}</span>')
            content_parts.append('</div>')
            
            # Location information
            location = event.get('location', 'Amsterdam')
            content_parts.append('<div class="event-info-line">')
            content_parts.append('<span class="event-icon">📍</span>')
            content_parts.append('<span class="event-label">Location:</span>')
            content_parts.append(f'<span class="event-value">{location}</span>')
            content_parts.append('</div>')
            
            # Source information
            content_parts.append('<div class="event-info-line">')
            content_parts.append('<span class="event-icon">🏛️</span>')
            content_parts.append('<span class="event-label">Source:</span>')
            content_parts.append(f'<span class="event-value">{event.get("source", "Official I amsterdam")}</span>')
            content_parts.append('</div>')
            
            # Tags if available
            if event.get('tags'):
                content_parts.append('<div class="event-info-line">')
                content_parts.append('<span class="event-icon">🏷️</span>')
                content_parts.append('<span class="event-label">Tags:</span>')
                content_parts.append('<span class="event-value">')
                content_parts.append(' • '.join(event['tags']))
                content_parts.append('</span>')
                content_parts.append('</div>')
            
            content_parts.append('</div>')  # Close event-details
            
            # Description section
            description = event.get('description', event['title'])
            
            if description and description != event['title']:
                content_parts.append('<div class="event-description">')
                content_parts.append('<div class="event-info-line">')
                content_parts.append('<span class="event-icon">ℹ️</span>')
                content_parts.append('<span class="event-label">Description:</span>')
                content_parts.append('</div>')
                content_parts.append(f'<p class="event-description-text">{description}</p>')
                content_parts.append('</div>')
            
            # Action section with clickable link
            content_parts.append('<div class="event-actions">')
            content_parts.append('<div class="event-info-line">')
            content_parts.append('<span class="event-icon">🌟</span>')
            content_parts.append('<span class="event-label">More Info:</span>')
            content_parts.append(f'<a href="{event["link"]}" target="_blank" rel="noopener" class="event-link">View Event Details on I amsterdam</a>')
            content_parts.append('</div>')
            content_parts.append('</div>')
            
            content_parts.append('</div>')  # Close amsterdam-event-card
            
            # Add CSS for better styling
            css_styles = '''
            <style>
            .amsterdam-event-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                margin: 15px 0;
                background: #fafafa;
                font-family: Arial, sans-serif;
            }
            .event-details {
                margin-bottom: 15px;
            }
            .event-info-line {
                display: flex;
                align-items: center;
                margin: 8px 0;
                line-height: 1.5;
            }
            .event-icon {
                font-size: 16px;
                margin-right: 8px;
                min-width: 24px;
            }
            .event-label {
                font-weight: bold;
                margin-right: 8px;
                color: #333;
                min-width: 80px;
            }
            .event-value {
                color: #555;
                flex: 1;
            }
            .event-description {
                margin: 15px 0;
                padding: 10px;
                background: #f0f0f0;
                border-radius: 4px;
            }
            .event-description-text {
                margin: 8px 0;
                line-height: 1.6;
                color: #444;
            }
            .event-actions {
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #ddd;
            }
            .event-link {
                color: #E31E24;
                text-decoration: none;
                font-weight: bold;
                padding: 8px 12px;
                background: #fff;
                border: 2px solid #E31E24;
                border-radius: 4px;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .event-link:hover {
                background: #E31E24;
                color: white;
            }
            </style>
            '''
            
            # Join all content
            full_content = css_styles + '\n'.join(content_parts)
            fe.description(full_content)
            
            # Also add image as enclosure for RSS readers that support it
            if event.get('image'):
                try:
                    fe.enclosure(url=event['image'], type='image/jpeg', length='0')
                except Exception as e:
                    logger.warning(f"Could not add enclosure for {event['title']}: {e}")
        
        # Generate the RSS feed
        rss_str = fg.rss_str(pretty=True)
        
        with open(output_file, 'wb') as f:
            f.write(rss_str)
        
        logger.info(f"RSS feed saved to {output_file}")

    def save_events_json(self, output_file="events.json"):
        """Save events as JSON for debugging/alternative use"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.events, f, indent=2, default=str, ensure_ascii=False)
        logger.info(f"Events data saved to {output_file}")

    def scrape_all(self):
        """Run all scrapers - prioritizing official I amsterdam source for current month events"""
        logger.info("Starting Amsterdam events scraping...")

        # Prioritize official I amsterdam agenda for current month events
        self.scrape_iamsterdam()

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
