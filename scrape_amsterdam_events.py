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

    def extract_event_image(self, event_url):
        """Extract the main image from an individual event page"""
        try:
            logger.info(f"Extracting image from: {event_url}")
            response = self.session.get(event_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Look for main event image - I amsterdam uses specific patterns
            image_selectors = [
                'img[alt*="Amsterdam"]',  # Images with Amsterdam in alt text
                'img[alt*="Elephant"]',  # Specific event images
                'img[alt*="Tentoonstelling"]',  # Exhibition images
                'img[alt*="Festival"]',  # Festival images
                "main img",  # Main content images
                ".hero img",  # Hero section images
                '[class*="image"] img',  # Any image container
                "article img:first-of-type",  # First image in article
            ]

            for selector in image_selectors:
                img_elem = soup.select_one(selector)
                if img_elem and img_elem.get("src"):
                    src = img_elem.get("src")
                    # Convert relative URLs to absolute
                    if src.startswith("/"):
                        src = urljoin(event_url, src)
                    # Skip very small images (likely icons)
                    if any(
                        skip in src.lower()
                        for skip in ["icon", "logo", "favicon", "social"]
                    ):
                        continue
                    logger.info(f"Found image: {src}")
                    return src

            # Fallback: look for any reasonable sized image
            for img in soup.find_all("img"):
                src = img.get("src", "")
                if src and not any(
                    skip in src.lower()
                    for skip in ["icon", "logo", "favicon", "social", "arrow"]
                ):
                    if src.startswith("/"):
                        src = urljoin(event_url, src)
                    return src

        except Exception as e:
            logger.warning(f"Error extracting image from {event_url}: {e}")

        return None

    def scrape_iamsterdam(self):
        """Scrape events from I Amsterdam website - official Amsterdam events agenda with images"""
        logger.info("Scraping I Amsterdam events agenda with images...")

        try:
            url = "https://www.iamsterdam.com/uit/agenda"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            events_found = 0

            logger.info("Looking for Amsterdam events in page content...")

            # Strategy 1: Look for links that contain event keywords and seem to be events
            all_links = soup.find_all("a", href=True)

            for link in all_links:
                try:
                    href = link.get("href", "")
                    title = link.get_text(strip=True)

                    # Skip navigation and empty links
                    if not title or len(title) < 10 or not href:
                        continue

                    # Look for event-related keywords in title
                    event_keywords = [
                        "amsterdam 750",
                        "tentoonstelling",
                        "concert",
                        "festival",
                        "museum",
                        "expositie",
                        "show",
                        "wandeling",
                        "tour",
                        "kunst",
                        "theater",
                        "muziek",
                        "evenement",
                        "activiteit",
                        "bezienswaardigheid",
                        "elephant parade",
                        "grachtenfestival",
                        "sail",
                        "canal parade",
                    ]

                    # Skip common navigation terms
                    skip_terms = [
                        "nederlands",
                        "english",
                        "deutsch",
                        "français",
                        "español",
                        "cookies",
                        "privacy",
                        "contact",
                        "volg ons",
                        "over ons",
                        "taal",
                        "language",
                        "filter",
                        "sorteren",
                        "ontdek amsterdam",
                        "i amsterdam store",
                        "city card",
                        "volgende",
                        "meer data",
                    ]

                    if any(skip in title.lower() for skip in skip_terms):
                        continue

                    # Check if this looks like an event
                    is_event = any(
                        keyword in title.lower() for keyword in event_keywords
                    )

                    # Also check if href looks event-related
                    if not is_event and href:
                        is_event = any(
                            keyword in href.lower()
                            for keyword in [
                                "event",
                                "agenda",
                                "activit",
                                "museum",
                                "festival",
                                "concert",
                                "tentoonstelling",
                            ]
                        )

                    if is_event:
                        full_link = urljoin(url, href)

                        # Extract image from individual event page
                        event_image = self.extract_event_image(full_link)

                        # Try to find additional context from parent elements
                        parent = link.find_parent(["div", "article", "section", "li"])
                        description = f"Discover this Amsterdam event: {title}"
                        date_info = "Check website for dates and times"
                        location = ""
                        tags = []

                        if parent:
                            parent_text = parent.get_text()

                            # Look for Amsterdam 750 tag
                            if "amsterdam 750" in parent_text.lower():
                                tags.append("Amsterdam 750 events")

                            # Look for gratis/free tag
                            if any(
                                term in parent_text.lower()
                                for term in ["gratis", "free"]
                            ):
                                tags.append("Gratis entree")

                            # Look for ToekomstTiendaagse tag
                            if "toekomsttiendaagse" in parent_text.lower():
                                tags.append("ToekomstTiendaagse")

                            # Look for date patterns in parent context
                            # Pattern for dates like "04 jun '25" or "4 juni 2025"
                            date_patterns = [
                                r"(\d{1,2})\s*(jan|feb|mar|apr|mei|jun|jul|aug|sep|okt|nov|dec)[a-z]*\s*\W?(\d{2,4})",
                                r"(\d{1,2})-(\d{1,2})-(\d{4})",
                                r"(\d{4})-(\d{1,2})-(\d{1,2})",
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
                                                "jan": "January",
                                                "feb": "February",
                                                "mar": "March",
                                                "mrt": "March",
                                                "apr": "April",
                                                "mei": "May",
                                                "jun": "June",
                                                "jul": "July",
                                                "aug": "August",
                                                "sep": "September",
                                                "okt": "October",
                                                "nov": "November",
                                                "dec": "December",
                                            }
                                            if month in month_map:
                                                date_info = f"{day} {month_map[month]} {year if len(year) == 4 else '20' + year}"
                                                break
                                        except:
                                            continue

                            # Look for location indicators
                            location_indicators = [
                                "amsterdam",
                                "museum",
                                "theater",
                                "concertgebouw",
                                "vondelpark",
                                "centrum",
                                "beursplein",
                            ]
                            for indicator in location_indicators:
                                if (
                                    indicator in parent_text.lower()
                                    and indicator not in title.lower()
                                ):
                                    location = indicator.title()
                                    break

                        # Create enhanced description with styling
                        description_parts = [
                            f"<div class='iamsterdam-event'>",
                            f"<h3 class='event-title'>{title}</h3>",
                        ]

                        if tags:
                            description_parts.append(f"<div class='event-tags'>")
                            for tag in tags:
                                description_parts.append(
                                    f"<span class='event-tag'>{tag}</span>"
                                )
                            description_parts.append(f"</div>")

                        description_parts.extend(
                            [
                                f"<div class='event-details'>",
                                f"<p class='event-date'>📅 {date_info}</p>",
                            ]
                        )

                        if location:
                            description_parts.append(
                                f"<p class='event-location'>📍 {location}</p>"
                            )

                        description_parts.extend(
                            [
                                f"<p class='event-source'>🏛️ Official I amsterdam event</p>",
                                f"</div>",
                                f"<div class='event-link'><a href='{full_link}' target='_blank'>View full details on I amsterdam</a></div>",
                                f"</div>",
                            ]
                        )

                        description = "\n".join(description_parts)

                        event_data = {
                            "title": title,
                            "link": full_link,
                            "description": description,
                            "source": "I Amsterdam Official",
                            "date_text": date_info,
                            "pub_date": datetime.now(timezone.utc),
                            "tags": tags,
                            "location": location,
                        }

                        # Add image if found
                        if event_image:
                            event_data["image"] = event_image

                        self.events.append(event_data)
                        events_found += 1

                        if events_found >= 15:  # Reasonable limit
                            break

                except Exception as e:
                    logger.warning(f"Error processing I Amsterdam link: {e}")
                    continue

                time.sleep(0.2)  # Be respectful with rate limiting

            # Strategy 2: If we didn't find many events, look for any structured content with keywords
            if events_found < 5:
                logger.info("Trying alternative content extraction...")

                # Look for text that contains Amsterdam 750 events (current special events)
                amsterdam_750_content = soup.find_all(
                    text=re.compile(r"amsterdam\s*750", re.I)
                )

                for content in amsterdam_750_content[:5]:
                    try:
                        parent = content.parent if hasattr(content, "parent") else None
                        if parent:
                            # Try to find the full event text
                            event_text = parent.get_text(strip=True)
                            if len(event_text) > 20 and len(event_text) < 200:
                                # Look for associated link
                                link_elem = parent.find("a", href=True)
                                event_link = (
                                    urljoin(url, link_elem["href"])
                                    if link_elem
                                    else url
                                )

                                # Try to extract image
                                event_image = (
                                    self.extract_event_image(event_link)
                                    if link_elem
                                    else None
                                )

                                description = f"""
                                <div class='iamsterdam-event'>
                                    <h3 class='event-title'>Amsterdam 750: {event_text[:100]}</h3>
                                    <div class='event-tags'>
                                        <span class='event-tag'>Amsterdam 750 events</span>
                                    </div>
                                    <div class='event-details'>
                                        <p class='event-date'>📅 Part of Amsterdam 750 celebrations</p>
                                        <p class='event-source'>🏛️ Official I amsterdam event</p>
                                    </div>
                                    <div class='event-description'>{event_text}</div>
                                    <div class='event-link'><a href='{event_link}' target='_blank'>View on I amsterdam</a></div>
                                </div>
                                """

                                event_data = {
                                    "title": f"Amsterdam 750: {event_text[:100]}",
                                    "link": event_link,
                                    "description": description,
                                    "source": "I Amsterdam Official",
                                    "date_text": "Part of Amsterdam 750 celebrations",
                                    "pub_date": datetime.now(timezone.utc),
                                    "tags": ["Amsterdam 750 events"],
                                }

                                if event_image:
                                    event_data["image"] = event_image

                                self.events.append(event_data)
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

            soup = BeautifulSoup(response.text, "html.parser")
            events_found = 0

            # Look for event listings
            event_items = soup.find_all(
                ["div", "article"], class_=re.compile(r"event|listing|card")
            )

            for item in event_items[:15]:  # Limit results
                try:
                    # Extract title
                    title_elem = item.find(
                        ["h1", "h2", "h3"], class_=re.compile(r"title|heading")
                    )
                    if not title_elem:
                        title_elem = item.find("a")

                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # Extract link
                    link_elem = item.find("a", href=True)
                    if link_elem:
                        link = urljoin(url, link_elem["href"])
                    else:
                        continue

                    # Extract description
                    desc_elem = item.find(
                        ["p", "div"], class_=re.compile(r"description|excerpt")
                    )
                    description = (
                        desc_elem.get_text(strip=True)
                        if desc_elem
                        else f"Time Out Amsterdam: {title}"
                    )

                    if title and link and len(title) > 5:  # Basic validation
                        self.events.append(
                            {
                                "title": title,
                                "link": link,
                                "description": description,
                                "source": "Time Out Amsterdam",
                                "date_text": "Check website for dates",
                                "pub_date": datetime.now(timezone.utc),
                            }
                        )
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

            soup = BeautifulSoup(response.text, "html.parser")
            events_found = 0

            # Look for event or activity links
            links = soup.find_all("a", href=True)

            for link in links[:10]:  # Limit to prevent spam
                try:
                    href = link.get("href", "")
                    title = link.get_text(strip=True)

                    # Filter for event-like content
                    if (
                        len(title) > 10
                        and any(
                            keyword in title.lower()
                            for keyword in [
                                "event",
                                "festival",
                                "show",
                                "concert",
                                "exhibition",
                                "museum",
                                "tour",
                                "market",
                            ]
                        )
                        and href
                        and not href.startswith("#")
                    ):

                        full_link = urljoin(url, href)

                        self.events.append(
                            {
                                "title": f"Amsterdam Activity: {title}",
                                "link": full_link,
                                "description": f"Discover this activity in Amsterdam: {title}",
                                "source": "Amsterdam.nl",
                                "date_text": "Ongoing",
                                "pub_date": datetime.now(timezone.utc),
                            }
                        )
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
            normalized_title = re.sub(
                r"[^a-zA-Z0-9\s]", "", event["title"].lower()
            ).strip()

            if normalized_title not in seen_titles and len(normalized_title) > 5:
                seen_titles.add(normalized_title)
                unique_events.append(event)

        original_count = len(self.events)
        self.events = unique_events
        logger.info(f"Removed {original_count - len(self.events)} duplicate events")

    def generate_rss_feed(self, output_file="events.xml"):
        """Generate RSS feed from collected events"""
        logger.info(f"Generating RSS feed with {len(self.events)} events...")

        fg = FeedGenerator()
        fg.title("Amsterdam Events Feed")
        fg.link(
            href="https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml"
        )
        fg.description(
            "Curated upcoming events and activities in Amsterdam from I amsterdam official agenda"
        )
        fg.language("en")
        fg.lastBuildDate(datetime.now(timezone.utc))
        fg.generator("Amsterdam Events Scraper v2.0")

        # Add each event as a feed entry
        for event in self.events:
            fe = fg.add_entry()
            fe.title(event["title"])
            fe.link(href=event["link"])

            # Create much cleaner and more readable HTML description
            description_html = f"""
            <div style="max-width: 600px; margin: 20px 0; font-family: Arial, sans-serif; line-height: 1.6;">
                
                {f'<img src="{event["image"]}" alt="{event["title"]}" style="width: 100%; max-width: 500px; height: 250px; object-fit: cover; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />' if event.get('image') else ''}
                
                <h2 style="color: #E31E24; font-size: 1.8em; margin: 0 0 15px 0; font-weight: bold; line-height: 1.3;">
                    {event['title']}
                </h2>
                
                {f'''<div style="margin: 15px 0;">
                    {" ".join([f'<span style="background: #E31E24; color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.85em; margin-right: 8px; margin-bottom: 5px; display: inline-block; font-weight: 500;">{tag}</span>' for tag in event.get("tags", [])])}
                </div>''' if event.get('tags') else ''}
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #E31E24;">
                    <div style="margin-bottom: 12px; font-size: 1.1em;">
                        <strong style="color: #E31E24;">📅 Date:</strong> 
                        <span style="color: #333;">{event.get('date', 'Check website for details')}</span>
                    </div>
                    <div style="margin-bottom: 12px; font-size: 1.1em;">
                        <strong style="color: #E31E24;">📍 Location:</strong> 
                        <span style="color: #333;">{event.get('location', 'Amsterdam')}</span>
                    </div>
                    <div style="font-size: 1.1em;">
                        <strong style="color: #E31E24;">🏛️ Source:</strong> 
                        <span style="color: #333;">Official I amsterdam</span>
                    </div>
                </div>
                
                <div style="margin: 20px 0; font-size: 1.05em; color: #555; line-height: 1.7;">
                    <p style="margin: 0;">{event['description'][:250]}{'...' if len(event['description']) > 250 else ''}</p>
                </div>
                
                <div style="margin-top: 25px; padding-top: 20px; border-top: 2px solid #f0f0f0; text-align: center;">
                    <a href="{event['link']}" target="_blank" style="
                        background: linear-gradient(135deg, #E31E24, #c41e3a); 
                        color: white; 
                        padding: 12px 30px; 
                        text-decoration: none; 
                        border-radius: 25px; 
                        font-weight: bold; 
                        font-size: 1.1em;
                        display: inline-block;
                        transition: all 0.3s ease;
                        box-shadow: 0 3px 6px rgba(227, 30, 36, 0.3);
                    ">
                        View Full Details on I amsterdam →
                    </a>
                </div>
                
                <div style="margin-top: 20px; text-align: center; font-size: 0.9em; color: #888; font-style: italic;">
                    Official Amsterdam event • Updated {datetime.now().strftime('%B %d, %Y')}
                </div>
                
            </div>
            """

            fe.description(description_html)
            fe.pubDate(event["pub_date"])

            # Add image as enclosure if available
            if event.get("image"):
                try:
                    # Estimate image size (WordPress expects this)
                    fe.enclosure(event["image"], 0, "image/jpeg")
                except Exception as e:
                    logger.warning(f"Could not add image enclosure: {e}")

        # Generate and save the RSS XML
        rss_str = fg.rss_str(pretty=True)
        with open(output_file, "wb") as f:
            f.write(rss_str)

        logger.info(f"RSS feed saved to {output_file}")
        return output_file

    def save_events_json(self, output_file="events.json"):
        """Save events as JSON for debugging/alternative use"""
        with open(output_file, "w", encoding="utf-8") as f:
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

            soup = BeautifulSoup(response.text, "html.parser")
            events_found = 0

            # Look for event cards
            event_cards = soup.find_all(
                ["div", "article"], attrs={"data-event-id": True}
            )  # Eventbrite uses data-event-id

            if not event_cards:
                # Fallback: look for links containing "events"
                event_links = soup.find_all("a", href=re.compile(r"/e/"))

                for link in event_links[:10]:
                    try:
                        title = link.get_text(strip=True)
                        href = link.get("href", "")

                        if len(title) > 10 and not any(
                            skip in title.lower()
                            for skip in ["sign up", "log in", "create"]
                        ):
                            full_link = urljoin(url, href)

                            self.events.append(
                                {
                                    "title": f"Eventbrite: {title}",
                                    "link": full_link,
                                    "description": f"Find this event on Eventbrite: {title}",
                                    "source": "Eventbrite Amsterdam",
                                    "date_text": "Check Eventbrite for dates",
                                    "pub_date": datetime.now(timezone.utc),
                                }
                            )
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
