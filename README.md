# 🇳🇱 Amsterdam Events Feed

**Automated Python scraper that collects Amsterdam event data and generates an RSS feed for easy WordPress integration.**

[![Scrape Amsterdam Events](https://github.com/USERNAME/amsterdam-events-feed/actions/workflows/scrape-events.yml/badge.svg)](https://github.com/USERNAME/amsterdam-events-feed/actions/workflows/scrape-events.yml)

## 🎯 What This Does

- **Scrapes** event data from multiple Amsterdam sources (I Amsterdam, Time Out, Amsterdam.nl)
- **Generates** a clean RSS feed updated daily
- **Automates** everything with GitHub Actions (zero maintenance)
- **Integrates** with WordPress using simple plugins (no coding required)

## 🚀 Quick Start for WordPress Site Owners

### Option 1: Display Events with RSS Plugin (Recommended)

1. **Install a WordPress RSS plugin:**
   - Go to **Plugins → Add New**
   - Search for "**Feedzy RSS Feeds**" and install it
   - Alternative: "**WP RSS Aggregator**"

2. **Add the feed:**
   - In WordPress admin: **Feedzy → Import Feeds → Add Feed**
   - Paste this URL: `https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml`
   - Click "Add Feed"

3. **Display events on your site:**
   - Copy the shortcode Feedzy provides (looks like `[feedzy-rss feeds="..." max="10"]`)
   - Paste it into any page, post, or widget
   - Choose a layout style (list, grid, or cards)

### Option 2: Auto-Import as WordPress Posts

1. **Use Feedzy Pro or WP RSS Aggregator Premium**
2. **Enable "Feed to Post" feature**
3. **Set up automatic import:** Events become real WordPress posts with SEO benefits

## 🛠️ Setup Instructions (For Developers)

### 1. Fork This Repository

1. Click "Fork" on this GitHub repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/amsterdam-events-feed.git`

### 2. Enable GitHub Actions

1. Go to your repository **Settings → Actions → General**
2. Under "Actions permissions," select "Allow all actions and reusable workflows"
3. The scraper will run automatically daily at 6 AM Amsterdam time

### 3. Test the Scraper Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scraper
python scrape_amsterdam_events.py

# Check output
ls -la events.xml events.json
```

### 4. Customize Sources (Optional)

Edit `scrape_amsterdam_events.py` to:
- Add new event sources
- Modify existing scrapers
- Change RSS feed metadata
- Adjust filtering rules

## 📊 Current Sources

| Source | Type | Update Frequency |
|--------|------|------------------|
| **I Amsterdam** | Official city events | Daily |
| **Time Out Amsterdam** | Curated activities | Daily |
| **Amsterdam.nl** | Municipal activities | Daily |

## 🔧 Technical Details

### Architecture

```
Amsterdam Websites → Python Scraper → RSS Feed → WordPress Plugin → Your Site
```

### Files

- `scrape_amsterdam_events.py` - Main scraper script
- `events.xml` - Generated RSS feed (auto-updated)
- `events.json` - Debug data (optional)
- `.github/workflows/scrape-events.yml` - Automation workflow

### Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `feedgen` - RSS generation
- `lxml` - XML processing

## 📅 RSS Feed Details

- **URL:** `https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml`
- **Format:** RSS 2.0
- **Update Schedule:** Daily at 6 AM Amsterdam time
- **Content:** Event title, description, source, and original link

## 🎨 WordPress Display Options

### Basic Display (Feedzy)
```
[feedzy-rss feeds="YOUR-FEED-URL" max="10" feed_title="no" target="_blank"]
```

### Grid Layout
```
[feedzy-rss feeds="YOUR-FEED-URL" max="12" columns="3" template="grid"]
```

### Custom Styling
The plugin generates clean HTML that you can style with CSS:

```css
.feedzy-rss .rss_item {
    border: 1px solid #ddd;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 8px;
}

.feedzy-rss .rss_item h3 {
    color: #e74c3c;
    font-size: 1.2em;
}
```

## 🔄 Automation Features

- ✅ **Daily scraping** at 6 AM Amsterdam time
- ✅ **Automatic deduplication** of events
- ✅ **Error handling** and logging
- ✅ **Smart rate limiting** to respect websites
- ✅ **GitHub Actions** for zero-maintenance operation

## 🚨 Troubleshooting

### No Events Showing
1. Check if the RSS feed loads: Open the feed URL in your browser
2. Verify the WordPress plugin is configured correctly
3. Look at the GitHub Actions logs for scraper errors

### Feed Not Updating
1. Check **Actions** tab in your GitHub repository
2. Manually trigger the workflow: **Actions → Scrape Amsterdam Events → Run workflow**
3. Review the workflow logs for errors

### WordPress Plugin Issues
1. Test with a different RSS URL to verify the plugin works
2. Check WordPress plugin logs or error console
3. Try an alternative RSS plugin (WP RSS Aggregator)

## 📝 Customization Ideas

### Add More Sources
```python
def scrape_your_source(self):
    """Add your custom scraper here"""
    # Your scraping logic
    pass
```

### Filter by Categories
```python
# In the scraping functions, add filtering:
if any(keyword in title.lower() for keyword in ['concert', 'festival']):
    # Only add music events
```

### Custom RSS Fields
```python
# Add more RSS fields:
fe.category('Music')  # Add categories
fe.author('Amsterdam Events')  # Add author
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use this for any purpose!

## 💡 Pro Tips

- **Test first:** Always verify scrapers work before deploying
- **Be respectful:** Don't overwhelm websites with requests
- **Monitor regularly:** Check GitHub Actions logs occasionally
- **Stay legal:** Respect robots.txt and terms of service
- **Backup plan:** Consider multiple WordPress RSS plugins

---

**Ready to get started?** Just fork this repo and follow the WordPress setup steps above! 🚀 