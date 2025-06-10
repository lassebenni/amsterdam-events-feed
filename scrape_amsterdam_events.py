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
import subprocess
import argparse
from markitdown import MarkItDown
from models import Event
import io
from email.utils import format_datetime
import markdown
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def translate_dutch_date_to_english(date_list: list[str]) -> list[str]:
    """Translates a list of Dutch date strings to English."""
    month_map = {
        'jan': 'Jan', 'feb': 'Feb', 'mrt': 'Mar', 'apr': 'Apr', 'mei': 'May', 'jun': 'Jun',
        'jul': 'Jul', 'aug': 'Aug', 'sep': 'Sep', 'okt': 'Oct', 'nov': 'Nov', 'dec': 'Dec'
    }
    day_map = {
        'ma': 'Mon', 'di': 'Tue', 'wo': 'Wed', 'do': 'Thu', 'vr': 'Fri', 'za': 'Sat', 'zo': 'Sun'
    }
    
    translated_dates = []
    for date_str in date_list:
        translated_str = date_str.lower()
        for nl, en in month_map.items():
            translated_str = translated_str.replace(nl, en)
        for nl, en in day_map.items():
            # Use word boundaries to avoid replacing parts of words
            translated_str = re.sub(r'\b' + nl + r'\b', en, translated_str)
        translated_dates.append(translated_str.title()) # Capitalize for better readability
    return translated_dates

def _build_html_content(event: Event) -> str:
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
    # Join the list of dates with a line break for display
    date_display = "<br>".join([markdown.markdown(d) for d in event.date_text])
    content_parts.append(f'<span class="event-value">{date_display}</span>')
    content_parts.append('</div>')

    # Price information
    price = markdown.markdown(event.price_text)
    if price:
        content_parts.append('<div class="event-info-line">')
        content_parts.append('<span class="event-icon">💰</span>')
        content_parts.append('<span class="event-label">Price:</span>')
        content_parts.append(f'<span class="event-value">{price}</span>')
        content_parts.append('</div>')
    
    # Location information
    location = event.location
    content_parts.append('<div class="event-info-line">')
    content_parts.append('<span class="event-icon">📍</span>')
    content_parts.append('<span class="event-label">Location:</span>')
    content_parts.append(f'<span class="event-value">{location}</span>')
    content_parts.append('</div>')
    
    # Source information
    content_parts.append('<div class="event-info-line">')
    content_parts.append('<span class="event-icon">🏛️</span>')
    content_parts.append('<span class="event-label">Source:</span>')
    content_parts.append(f'<span class="event-value">{event.source}</span>')
    content_parts.append('</div>')
    
    # Tags if available
    if event.tags:
        content_parts.append('<div class="event-info-line">')
        content_parts.append('<span class="event-icon">🏷️</span>')
        content_parts.append('<span class="event-label">Tags:</span>')
        content_parts.append('<span class="event-value">')
        content_parts.append(' • '.join(event.tags))
        content_parts.append('</span>')
        content_parts.append('</div>')
    
    content_parts.append('</div>')  # Close event-details
    
    # Description section
    description_html = event.description
    
    if description_html and description_html != event.title:
        content_parts.append('<div class="event-description">')
        content_parts.append('<div class="event-info-line">')
        content_parts.append('<span class="event-icon">ℹ️</span>')
        content_parts.append('<span class="event-label">Description:</span>')
        content_parts.append('</div>')
        content_parts.append(f'<p class="event-description-text">{description_html}</p>')
        content_parts.append('</div>')
    
    # Action section with clickable link
    content_parts.append('<div class="event-actions">')
    content_parts.append('<div class="event-info-line">')
    content_parts.append('<span class="event-icon">🌟</span>')
    content_parts.append('<span class="event-label">More Info:</span>')
    content_parts.append(f'<a href="{str(event.link)}" target="_blank" rel="noopener" class="event-link">View Event Details on I amsterdam</a>')
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
    html_content = css_styles + '\n'.join(content_parts)
    return html_content

class AmsterdamEventsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        self.events: list[Event] = []
        self.md_converter = MarkItDown()

    def _parse_event_from_markdown(self, markdown_text: str) -> dict:
        """Extract event details from a markdown string using regex."""
        data = {
            "date_text": ["Check website for dates"],
            "price_text": "Check website for prices",
            "description": None,
        }

        # Isolate the "Data" block first to avoid capturing stray dates
        data_block_pattern = re.compile(r"## Data\n\n(.*?)\n\n##", re.IGNORECASE | re.DOTALL)
        data_block_match = data_block_pattern.search(markdown_text)
        
        search_text = markdown_text # Default to searching the whole text
        if data_block_match:
            search_text = data_block_match.group(1)
            logger.info("Successfully isolated the 'Data' block for date searching.")

        # Date parsing
        # Looks for a line like "di 10 jun" or "10 jun - 12 jun"
        date_pattern = re.compile(r"^\s*(\b(di|wo|do|vr|za|zo|ma)\b.*|.*\d{1,2}\s+(jan|feb|mrt|apr|mei|jun|jul|aug|sep|okt|nov|dec).*)$", re.IGNORECASE | re.MULTILINE)
        dates_found = date_pattern.findall(search_text)
        if dates_found:
            # Extract the first group from each tuple in the findall result
            cleaned_dates = [match[0].strip() for match in dates_found]
            # Translate dates to English before returning
            translated_dates = translate_dutch_date_to_english(cleaned_dates)
            data["date_text"] = translated_dates
            logger.info(f"Found and translated {len(translated_dates)} dates: {translated_dates}")

        # Price parsing
        # Looks for a line containing "€" or "Gratis"
        price_pattern = re.compile(r"^(.*(€|Gratis|Free).*)$", re.IGNORECASE | re.MULTILINE)
        price_match = price_pattern.search(markdown_text)
        if price_match:
            data["price_text"] = price_match.group(1).strip()
            logger.info(f"Found price: {data['price_text']}")

        # Description parsing
        # Clean the markdown to remove syntax like links and images before extracting text.
        
        # Remove headers first
        clean_text = re.sub(r'^\s*#+.*$', '', markdown_text, flags=re.MULTILINE)
        
        # Remove image markdown ![...](...)
        clean_text = re.sub(r'!\[.*?\]\(.*?\)', '', clean_text)
        
        # Convert markdown links to plain text: [text](url) -> text
        clean_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean_text)

        # Remove horizontal rules
        clean_text = re.sub(r'^\s*[-*_]{3,}\s*$', '', clean_text, flags=re.MULTILINE)

        # Split into paragraphs and find the first substantive one.
        paragraphs = re.split(r'\n\s*\n', clean_text)
        description = "Check website for description."
        for p in paragraphs:
            p_clean = p.strip().replace('\n', ' ') # Join lines within a paragraph
            # A good description should be substantive.
            if len(p_clean) > 80:
                description = p_clean
                break # Found a good candidate

        # Final cleanup to normalize whitespace
        data["description"] = re.sub(r'\s+', ' ', description).strip()


        return data

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

    async def scrape_iamsterdam_playwright(self, limit=None):
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

                if limit:
                    logger.info(f"Applying limit: scraping a maximum of {limit} events.")
                    event_urls = event_urls[:limit]

                async with async_playwright() as p_inner:
                    browser_inner = await p_inner.chromium.launch()
                    context_inner = await browser_inner.new_context()

                    for url in event_urls:
                        try:
                            page = await context_inner.new_page()
                            await page.goto(url, wait_until='domcontentloaded')

                            # Handle cookie consent
                            try:
                                allow_button = await page.query_selector('button:has-text("Allow all")')
                                if allow_button:
                                    await allow_button.click()
                                    logger.info("Accepted cookie consent.")
                                    # Wait for the banner to disappear
                                    await page.wait_for_selector('button:has-text("Allow all")', state='hidden')
                            except Exception as e:
                                logger.warning(f"Could not handle cookie consent on {url}: {e}")

                            title = await page.title()
                            
                            # Try to find a more specific title within the page
                            h1_title = await page.query_selector('h1')
                            if h1_title:
                                title = await h1_title.text_content()
                            
                            # New approach: get HTML, convert to Markdown, then parse
                            main_content_html = ""
                            main_element = await page.query_selector('main')
                            if main_element:
                                main_content_html = await main_element.inner_html()

                            if not main_content_html:
                                logger.warning(f"Could not find main content for {url}")
                                continue

                            # Use markitdown to convert HTML to Markdown
                            # It expects a file-like object, so we use io.BytesIO
                            html_stream = io.BytesIO(main_content_html.encode('utf-8'))
                            result = self.md_converter.convert(html_stream)
                            markdown_text = result.text_content

                            parsed_data = self._parse_event_from_markdown(markdown_text)

                            description = parsed_data.get("description")

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
                            
                            event_data = Event(
                                title=title.strip(),
                                link=url,
                                description=description,
                                source="I Amsterdam Official",
                                date_text=parsed_data.get("date_text", ["Check website for dates"]),
                                price_text=parsed_data.get("price_text", "Check website for prices"),
                                pub_date=datetime.now(timezone.utc),
                                image=event_image
                            )

                            if not any(e.link == event_data.link for e in self.events):
                                self.events.append(event_data)
                            
                            await page.close()

                        except Exception as e:
                            logger.warning(f"Error processing page {url}: {e}")
                            if 'page' in locals() and not page.is_closed():
                                await page.close()
                            continue
                    
                    await browser_inner.close()

                logger.info(f"Finished processing. Found {len(self.events)} unique events.")

        except Exception as e:
            logger.error(f"Error scraping I Amsterdam agenda with Playwright: {e}")

    def scrape_iamsterdam(self, limit=None):
        """Scrape events from I Amsterdam website - official Amsterdam events agenda with images"""
        asyncio.run(self.scrape_iamsterdam_playwright(limit=limit))

    def deduplicate_events(self):
        """Remove duplicate events based on title similarity"""
        logger.info("Removing duplicate events...")

        unique_events = []
        seen_titles = set()

        for event in self.events:
            # Create a normalized title for comparison
            normalized_title = re.sub(
                r"[^a-zA-Z0-9\s]", "", event.title.lower()
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
        
        rss = ET.Element("rss", version="2.0", attrib={"xmlns:content": "http://purl.org/rss/1.0/modules/content/"})
        channel = ET.SubElement(rss, "channel")

        title = ET.SubElement(channel, "title")
        title.text = "Amsterdam Events Feed"
        
        link = ET.SubElement(channel, "link")
        link.text = "https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml"

        ET.SubElement(channel, "link", attrib={"rel": "self", "type": "application/rss+xml", "href": "https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml"})
        
        description = ET.SubElement(channel, "description")
        description.text = "Curated upcoming events and activities in Amsterdam from I amsterdam official agenda"
        
        language = ET.SubElement(channel, "language")
        language.text = "en"
        
        lastBuildDate = ET.SubElement(channel, "lastBuildDate")
        lastBuildDate.text = format_datetime(datetime.now(timezone.utc))
        
        generator = ET.SubElement(channel, "generator")
        generator.text = "Amsterdam Events Scraper v10.0"

        for event in self.events:
            item = ET.SubElement(channel, "item")
            
            item_title = ET.SubElement(item, "title")
            item_title.text = event.title
            
            item_link = ET.SubElement(item, "link")
            item_link.text = str(event.link)
            
            item_pubDate = ET.SubElement(item, "pubDate")
            item_pubDate.text = format_datetime(event.pub_date)

            item_guid = ET.SubElement(item, "guid", isPermaLink="false")
            item_guid.text = str(event.link)

            item_description = ET.SubElement(item, "description")
            item_description.text = event.description

            content_encoded = ET.SubElement(item, "content:encoded")
            content_encoded.text = f"__CDATA_PLACEHOLDER_{event.link}__"
            
            # Also add image as enclosure for RSS readers that support it
            if event.image:
                try:
                    ET.SubElement(item, "enclosure", url=str(event.image), type='image/jpeg', length='0')
                except Exception as e:
                    logger.warning(f"Could not add enclosure for {event.title}: {e}")
        
        # Generate the RSS feed
        xml_str = ET.tostring(rss, encoding='unicode')
        
        for event in self.events:
            html_content = _build_html_content(event)
            cdata_placeholder = f"__CDATA_PLACEHOLDER_{event.link}__"
            xml_str = xml_str.replace(cdata_placeholder, f"<![CDATA[{html_content}]]>")

        with open(output_file, 'w') as f:
            f.write(xml_str)

    def save_events_json(self, output_file="events.json"):
        """Save events as JSON for debugging/alternative use"""
        # Create a list of dictionaries from the Pydantic models
        events_dict = [event.model_dump(mode='json') for event in self.events]
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(events_dict, f, indent=2, ensure_ascii=False)
        logger.info(f"Events data saved to {output_file}")

    def scrape_all(self, limit=None):
        """Run all scrapers - prioritizing official I amsterdam source for current month events"""
        logger.info("Starting Amsterdam events scraping...")

        # Prioritize official I amsterdam agenda for current month events
        self.scrape_iamsterdam(limit=limit)

        # Clean up the data
        self.deduplicate_events()

        logger.info(f"Scraping complete. Total events collected: {len(self.events)}")

        return self.events


def publish_to_github():
    """Commit and push the updated feed files to GitHub."""
    logger.info("Publishing updated feed to GitHub...")
    try:
        # Configure Git user
        subprocess.run(['git', 'config', 'user.name', 'Automated Scraper'], check=True)
        subprocess.run(['git', 'config', 'user.email', 'scraper@example.com'], check=True)

        # Add the generated files
        subprocess.run(['git', 'add', 'events.xml', 'events.json'], check=True)
        
        # Check for changes
        status_result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if not status_result.stdout.strip():
            logger.info("No changes to commit. Feed is already up-to-date.")
            return

        # Commit the changes
        commit_message = f"feed: Auto-update event feed on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push the changes
        subprocess.run(['git', 'push'], check=True)
        
        logger.info("Successfully published the new feed to GitHub.")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to publish to GitHub: {e}")
        logger.error(f"Git command output:\n{e.stderr}")
    except FileNotFoundError:
        logger.error("Git command not found. Please ensure Git is installed and in your PATH.")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Scrape Amsterdam events and generate an RSS feed.")
    parser.add_argument("--limit", type=int, help="Limit the number of events to scrape for testing.")
    args = parser.parse_args()

    scraper = AmsterdamEventsScraper()

    # Scrape all sources
    events = scraper.scrape_all(limit=args.limit)

    if events:
        # Generate RSS feed
        scraper.generate_rss_feed()

        # Save JSON for debugging
        scraper.save_events_json()

        print(f"✅ Successfully generated feed with {len(events)} events")
        print("📄 Files created: events.xml, events.json")
        
        # Publish the new feed to GitHub
        publish_to_github()

        print("🔗 Ready to use with WordPress RSS plugins!")
    else:
        print("❌ No events found. Check the scrapers.")


if __name__ == "__main__":
    main()
