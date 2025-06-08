#!/usr/bin/env python3
"""
Test script for Amsterdam Events Scraper
Use this to test individual scrapers or debug issues
"""

from scrape_amsterdam_events import AmsterdamEventsScraper
import json

def test_individual_scrapers():
    """Test each scraper individually"""
    scraper = AmsterdamEventsScraper()
    
    print("🧪 Testing Individual Scrapers\n")
    
    # Test I Amsterdam
    print("Testing I Amsterdam scraper...")
    initial_count = len(scraper.events)
    scraper.scrape_iamsterdam()
    iamsterdam_events = len(scraper.events) - initial_count
    print(f"Found {iamsterdam_events} events from I Amsterdam\n")
    
    # Test Time Out
    print("Testing Time Out scraper...")
    initial_count = len(scraper.events)
    scraper.scrape_timeout_amsterdam()
    timeout_events = len(scraper.events) - initial_count
    print(f"Found {timeout_events} events from Time Out\n")
    
    # Test Amsterdam.nl
    print("Testing Amsterdam.nl scraper...")
    initial_count = len(scraper.events)
    scraper.scrape_amsterdam_nl()
    amsterdam_nl_events = len(scraper.events) - initial_count
    print(f"Found {amsterdam_nl_events} events from Amsterdam.nl\n")
    
    # Test Eventbrite
    print("Testing Eventbrite scraper...")
    initial_count = len(scraper.events)
    scraper.scrape_eventbrite_amsterdam()
    eventbrite_events = len(scraper.events) - initial_count
    print(f"Found {eventbrite_events} events from Eventbrite\n")
    
    # Summary
    print(f"📊 Summary:")
    print(f"Total events before deduplication: {len(scraper.events)}")
    
    scraper.deduplicate_events()
    print(f"Total events after deduplication: {len(scraper.events)}")
    
    # Show sample events
    if scraper.events:
        print(f"\n📋 Sample Events:")
        for i, event in enumerate(scraper.events[:3]):
            print(f"{i+1}. {event['title']} ({event['source']})")
            print(f"   Link: {event['link']}")
            print(f"   Date: {event['date_text']}\n")
    
    return scraper.events

def test_rss_generation():
    """Test RSS feed generation"""
    print("🔄 Testing RSS Generation\n")
    
    scraper = AmsterdamEventsScraper()
    events = scraper.scrape_all()
    
    if events:
        scraper.generate_rss_feed('test_events.xml')
        scraper.save_events_json('test_events.json')
        
        print(f"✅ Generated test RSS feed with {len(events)} events")
        print("Files created: test_events.xml, test_events.json")
        
        # Show RSS content sample
        try:
            with open('test_events.xml', 'r', encoding='utf-8') as f:
                rss_content = f.read()
                print(f"\n📄 RSS feed size: {len(rss_content)} characters")
                
                # Check if it's valid XML
                if '<?xml' in rss_content and '</rss>' in rss_content:
                    print("✅ RSS feed appears to be valid XML")
                else:
                    print("❌ RSS feed may be malformed")
                    
        except Exception as e:
            print(f"❌ Error reading RSS file: {e}")
    else:
        print("❌ No events found, cannot test RSS generation")

def show_events_json():
    """Display events in readable JSON format"""
    try:
        with open('test_events.json', 'r', encoding='utf-8') as f:
            events = json.load(f)
            
        print(f"\n📋 All Events ({len(events)}):")
        print("=" * 50)
        
        for i, event in enumerate(events, 1):
            print(f"{i}. {event['title']}")
            print(f"   Source: {event['source']}")
            print(f"   Date: {event['date_text']}")
            print(f"   Link: {event['link']}")
            print(f"   Description: {event['description'][:100]}...")
            print()
            
    except FileNotFoundError:
        print("❌ test_events.json not found. Run test_rss_generation() first.")
    except Exception as e:
        print(f"❌ Error reading events: {e}")

if __name__ == "__main__":
    print("🇳🇱 Amsterdam Events Scraper - Test Suite")
    print("=" * 50)
    
    # Run all tests
    test_individual_scrapers()
    test_rss_generation()
    show_events_json()
    
    print("\n🎯 Test complete!")
    print("Next steps:")
    print("1. Check test_events.xml in your browser")
    print("2. Use the RSS URL in WordPress RSS plugins")
    print("3. Push to GitHub to activate automation") 