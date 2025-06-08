# 🔌 WordPress Setup Guide

**5-minute setup to display Amsterdam events on your WordPress site**

## Step 1: Install RSS Plugin

### Option A: Feedzy RSS Feeds (Recommended)
1. Log into your WordPress admin dashboard
2. Go to **Plugins → Add New**
3. Search for "**Feedzy RSS Feeds**"
4. Click **Install Now** then **Activate**

### Option B: WP RSS Aggregator (Alternative)
1. Go to **Plugins → Add New**
2. Search for "**WP RSS Aggregator**"
3. Click **Install Now** then **Activate**

## Step 2: Add the Events Feed

### For Feedzy RSS Feeds:
1. In WordPress admin, go to **Feedzy → Import Feeds**
2. Click **Add Feed**
3. Paste this URL:
   ```
   https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml
   ```
4. Click **Add Feed**

### For WP RSS Aggregator:
1. Go to **RSS Aggregator → Feed Sources**
2. Click **Add New**
3. Enter a name: "Amsterdam Events"
4. Paste the feed URL (same as above)
5. Click **Publish**

## Step 3: Display Events

### Using Shortcodes (Easy)

Add events to any page or post by pasting one of these shortcodes:

**Basic List:**
```
[feedzy-rss feeds="YOUR-FEED-URL" max="10" feed_title="no"]
```

**Nice Grid (3 columns):**
```
[feedzy-rss feeds="YOUR-FEED-URL" max="12" columns="3" template="grid"]
```

**Card Layout:**
```
[feedzy-rss feeds="YOUR-FEED-URL" max="8" template="card"]
```

### Using Blocks (WordPress 5.0+)

1. Edit a page or post
2. Add a **Shortcode Block**
3. Paste one of the shortcodes above

### Using Widgets

1. Go to **Appearance → Widgets**
2. Add a **Custom HTML** widget
3. Paste a shortcode

## Step 4: Styling (Optional)

### Custom CSS
Go to **Appearance → Customize → Additional CSS** and add:

```css
/* Make events look nice */
.feedzy-rss .rss_item {
    border: 1px solid #e1e1e1;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 8px;
    background: #fafafa;
}

.feedzy-rss .rss_item h3 {
    color: #d63384;
    margin-top: 0;
}

.feedzy-rss .rss_item .rss_content {
    color: #666;
    line-height: 1.6;
}

/* Grid layout improvements */
.feedzy-rss.feedzy-default .rss_item {
    display: block;
    margin-bottom: 30px;
}
```

## Advanced Options

### Auto-Import as Posts (Premium Features)

If you upgrade to **Feedzy Pro** or **WP RSS Aggregator Premium**:

1. Enable "Feed to Post" feature
2. Set events to import as **Posts** or **Events** (custom post type)
3. Configure automatic import schedule
4. Events become real WordPress content with SEO benefits

### Popular Premium Features:
- **Automatic imports** every hour/day
- **Custom post types** (Events, Activities)
- **Featured images** extraction
- **Category assignments**
- **Content filtering** and formatting

## Troubleshooting

### ❌ "No items to display"
- Check if the feed URL loads in your browser
- Verify your GitHub username in the URL
- Make sure the GitHub repository is public

### ❌ Events not updating
- The feed updates daily at 6 AM Amsterdam time
- GitHub Actions must be enabled in the repository
- Check the "Actions" tab in GitHub for errors

### ❌ Plugin not working
- Try deactivating and reactivating the plugin
- Test with a different RSS feed (like a news site)
- Check WordPress error logs
- Try the alternative plugin

### ❌ Styling looks bad
- Each WordPress theme styles RSS content differently
- Add custom CSS (see styling section above)
- Try different shortcode templates
- Consider using a different theme

## Pro Tips

1. **Start simple:** Use the basic shortcode first, then customize
2. **Test on staging:** Try new shortcodes on a test page first
3. **Monitor performance:** Too many events can slow page loading
4. **Cache friendly:** RSS feeds work well with caching plugins
5. **Mobile responsive:** Most RSS plugins are mobile-friendly by default

## Example Shortcodes for Different Layouts

**Minimal (just titles and links):**
```
[feedzy-rss feeds="YOUR-FEED-URL" max="5" meta="no" summary="no"]
```

**With descriptions:**
```
[feedzy-rss feeds="YOUR-FEED-URL" max="8" summarylength="100"]
```

**Open in new tabs:**
```
[feedzy-rss feeds="YOUR-FEED-URL" max="10" target="_blank"]
```

**Different sorting:**
```
[feedzy-rss feeds="YOUR-FEED-URL" max="10" sort="date_desc"]
```

---

**Need help?** Contact your website developer or check the plugin documentation!

🎯 **Result:** Fresh Amsterdam events automatically updating on your WordPress site every day! 