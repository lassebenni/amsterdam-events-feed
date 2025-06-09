# 🧪 Local WordPress Testing Guide

**Test the Amsterdam Events RSS feed with a local WordPress installation**

## 🚀 Quick Setup (One Command)

```bash
./setup-local-wordpress.sh
```

This will automatically:
- Start WordPress and MySQL containers
- Set up the database
- Open WordPress in your browser

## 📋 Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Start the containers
docker compose up -d

# Check status
docker compose ps

# View logs if needed
docker compose logs wordpress
```

## 🌐 Access URLs

- **WordPress Site:** http://localhost:8080
- **WordPress Admin:** http://localhost:8080/wp-admin
- **phpMyAdmin:** http://localhost:8081 (database management)

## 🔧 WordPress Initial Setup

1. **Open WordPress:** http://localhost:8080
2. **Choose Language:** English (United States)
3. **Site Information:**
   - Site Title: `Amsterdam Events Test`
   - Username: `admin` (or your choice)
   - Password: Choose a strong password
   - Email: Your email address
4. **Click:** "Install WordPress"

## 📦 Install RSS Plugin

### Method 1: WordPress Admin (Recommended)
1. **Login:** http://localhost:8080/wp-admin
2. **Go to:** Plugins → Add New
3. **Search:** "Feedzy RSS Feeds"
4. **Install and Activate** the plugin

### Method 2: Download Plugin Manually
```bash
# Download Feedzy plugin (if needed)
curl -o feedzy-rss-feeds.zip https://downloads.wordpress.org/plugin/feedzy-rss-feeds.latest-stable.zip

# Extract to plugins directory
# (WordPress container handles this automatically via admin)
```

## 🔗 Add Amsterdam Events Feed

### Step 1: Add Feed Source
1. **In WordPress Admin:** Feedzy → Import Feeds
2. **Click:** "Add Feed"
3. **Feed URL:** 
   ```
   https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml
   ```
4. **Feed Name:** "Amsterdam Events"
5. **Click:** "Add Feed"

### Step 2: Display Events
1. **Create New Page:** Pages → Add New
2. **Page Title:** "Amsterdam Events"
3. **Add Shortcode Block**
4. **Paste Shortcode:**
   ```
   [feedzy-rss feeds="https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml" max="10" feed_title="no" target="_blank"]
   ```
5. **Publish** the page

## 🎨 Test Different Display Styles

### Basic List
```
[feedzy-rss feeds="https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml" max="5"]
```

### Grid Layout (3 columns)
```
[feedzy-rss feeds="https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml" max="9" columns="3" template="grid"]
```

### Card Style
```
[feedzy-rss feeds="https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml" max="6" template="card"]
```

### Custom Styling
Add to **Appearance → Customize → Additional CSS:**
```css
/* Amsterdam Events Styling */
.feedzy-rss .rss_item {
    border: 2px solid #e74c3c;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 10px;
    background: linear-gradient(135deg, #fff5f5, #fff);
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.feedzy-rss .rss_item h3 {
    color: #c0392b;
    margin-top: 0;
    font-size: 1.3em;
}

.feedzy-rss .rss_item .rss_content {
    color: #555;
    line-height: 1.6;
}

.feedzy-rss .rss_item a {
    background: #e74c3c;
    color: white;
    padding: 8px 16px;
    text-decoration: none;
    border-radius: 5px;
    display: inline-block;
    margin-top: 10px;
}

.feedzy-rss .rss_item a:hover {
    background: #c0392b;
}
```

## 🧪 Testing Checklist

### ✅ Basic Functionality
- [ ] WordPress loads at http://localhost:8080
- [ ] Can login to admin panel
- [ ] Feedzy plugin installs successfully
- [ ] RSS feed URL can be added to Feedzy
- [ ] Events display on the frontend

### ✅ RSS Feed Content
- [ ] 4 Amsterdam events appear
- [ ] Event titles are readable
- [ ] Event links work (open Eventbrite pages)
- [ ] Event descriptions show
- [ ] Dates/sources are displayed

### ✅ Display Options
- [ ] Basic list format works
- [ ] Grid layout displays correctly
- [ ] Card template looks good
- [ ] Custom CSS styling applies
- [ ] Links open in new tabs

### ✅ Advanced Features
- [ ] Feed updates when scraper runs
- [ ] Multiple shortcodes work on same page
- [ ] Different max event counts work
- [ ] RSS feed validates (check source)

## 🔍 Troubleshooting

### ❌ "No items to display"
```bash
# Check if RSS feed is accessible
curl -I https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml

# Should return HTTP 200
```

### ❌ WordPress not loading
```bash
# Check container status
docker compose ps

# View logs
docker compose logs wordpress

# Restart containers
docker compose restart
```

### ❌ Database connection errors
```bash
# Check MySQL container
docker compose logs db

# Reset containers
docker compose down
docker compose up -d
```

### ❌ Plugin installation fails
1. **Download manually:** https://wordpress.org/plugins/feedzy-rss-feeds/
2. **Upload via:** Plugins → Add New → Upload Plugin

## 📊 Performance Testing

### Test RSS Feed Speed
```bash
# Test feed response time
time curl -s https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml > /dev/null

# Should be under 1 second
```

### Test WordPress Load Time
1. **Install Plugin:** Query Monitor (for debugging)
2. **Check:** Database queries and load times
3. **Optimize:** Caching plugins if needed

## 🛑 Cleanup

### Stop Containers (Keep Data)
```bash
docker compose down
```

### Remove Everything (Delete Data)
```bash
docker compose down -v
docker system prune -f
```

### Remove Images (Full Cleanup)
```bash
docker compose down -v --rmi all
```

## 🎯 Success Criteria

**✅ Test Passed When:**
1. WordPress loads without errors
2. Feedzy plugin installs and activates
3. RSS feed can be added to Feedzy
4. 4 Amsterdam events display correctly
5. Event links work and open Eventbrite
6. Different display styles work
7. Custom CSS applies correctly
8. No PHP errors in logs

**🎉 Ready for Production When:**
- All tests pass locally
- RSS feed validates correctly
- WordPress site performs well
- Events update automatically

---

**Need Help?** Check the troubleshooting section or review the WordPress/Docker logs for detailed error messages. 