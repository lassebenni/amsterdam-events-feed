# 🚀 Quick Start Guide

**Get Amsterdam events on your WordPress site in 5 minutes!**

## For WordPress Site Owners (Non-Technical)

### Step 1: Install RSS Plugin
1. WordPress Admin → **Plugins** → **Add New**
2. Search: **"Feedzy RSS Feeds"**
3. **Install** and **Activate**

### Step 2: Add Events Feed
1. **Feedzy** → **Import Feeds** → **Add Feed**
2. Paste URL: `https://raw.githubusercontent.com/lassebenninga/amsterdam-events-feed/main/events.xml`
3. **Add Feed**

### Step 3: Display Events
Add this shortcode to any page/post:
```
[feedzy-rss feeds="https://raw.githubusercontent.com/lassebenninga/amsterdam-events-feed/main/events.xml" max="10" feed_title="no"]
```

**Done!** Events update automatically every day at 6 AM.

---

## For Developers

### Test Locally
```bash
git clone https://github.com/lassebenninga/amsterdam-events-feed.git
cd amsterdam-events-feed
pip install -r requirements.txt
python3 scrape_amsterdam_events.py
```

### Customize
- Edit `scrape_amsterdam_events.py` to add sources
- Modify RSS feed metadata
- Adjust scraping frequency in `.github/workflows/scrape-events.yml`

### Deploy
1. Fork this repository
2. Enable GitHub Actions
3. Update URLs in README.md with your username
4. Push changes

---

## Current Status

✅ **Working Sources:**
- Eventbrite Amsterdam (4+ events found)

⚠️ **Needs Improvement:**
- I Amsterdam (website structure changed)
- Time Out Amsterdam (URL needs updating)
- Amsterdam.nl (needs better selectors)

## RSS Feed URL
```
https://raw.githubusercontent.com/lassebenninga/amsterdam-events-feed/main/events.xml
```

## Support

- **WordPress Issues:** Check WORDPRESS_SETUP.md
- **Technical Issues:** Check README.md
- **Testing:** Run `python3 test_scraper.py`

---

**🎯 Result:** Fresh Amsterdam events automatically on your website! 