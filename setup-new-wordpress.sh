#!/bin/bash

echo "🚀 Setting up fresh WordPress for Amsterdam Events with RSS image support..."

# Stop any existing containers
echo "Stopping existing containers..."
docker compose -f docker-compose-new.yml down --volumes 2>/dev/null || true

# Clean up old containers if they exist
docker container rm amsterdam-events-wp amsterdam-events-db amsterdam-events-phpmyadmin 2>/dev/null || true

# Create necessary directories
mkdir -p wp-custom wp-uploads

# Start the containers
echo "Starting new WordPress containers..."
docker compose -f docker-compose-new.yml up -d

# Wait for WordPress to be ready
echo "Waiting for WordPress to initialize (60 seconds)..."
sleep 60

# Function to run wp-cli commands
wp_cli() {
    docker compose -f docker-compose-new.yml exec -T wordpress wp --allow-root "$@"
}

# Install WordPress
echo "Installing WordPress..."
wp_cli core install \
    --url="http://localhost:8081" \
    --title="Amsterdam Events Hub" \
    --admin_user="admin" \
    --admin_password="admin123" \
    --admin_email="admin@amsterdamevents.local" \
    --skip-email

# Install and activate essential plugins for RSS with images
echo "Installing RSS plugins with image support..."

# Install multiple RSS plugins to test which works best
wp_cli plugin install feedzy-rss-feeds --activate
wp_cli plugin install wp-rss-aggregator --activate  
wp_cli plugin install rss-import --activate
wp_cli plugin install super-rss-reader --activate

# Install additional helpful plugins
wp_cli plugin install classic-editor --activate
wp_cli plugin install advanced-custom-fields --activate

# Create a custom theme directory
echo "Setting up custom theme..."
cat > wp-custom/style.css << 'EOF'
/*
Theme Name: Amsterdam Events Theme
Description: Custom theme for Amsterdam Events
Version: 1.0
*/

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
}

.amsterdam-events {
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
}

.event-item {
    border: 1px solid #ddd;
    margin: 20px 0;
    padding: 20px;
    border-radius: 8px;
    background: #f9f9f9;
}

.event-title {
    color: #E31E24;
    font-size: 1.2em;
    font-weight: bold;
    margin-bottom: 10px;
}

.event-image {
    max-width: 300px;
    height: auto;
    margin: 10px 0;
    border-radius: 5px;
    display: block;
}

.rss-item-image img {
    max-width: 300px !important;
    height: auto !important;
    border-radius: 5px;
    margin: 10px 0;
}

.feedzy-rss img {
    max-width: 300px !important;
    height: auto !important;
    border-radius: 5px;
}

.event-description {
    line-height: 1.6;
    color: #555;
    margin: 10px 0;
}

.event-link {
    background: #E31E24;
    color: white;
    padding: 8px 16px;
    text-decoration: none;
    border-radius: 4px;
    display: inline-block;
    margin-top: 10px;
}

.event-link:hover {
    background: #c01a21;
    color: white;
    text-decoration: none;
}
EOF

cat > wp-custom/index.php << 'EOF'
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?php wp_title('|', true, 'right'); ?></title>
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
    <div class="amsterdam-events">
        <header>
            <h1><?php bloginfo('name'); ?></h1>
            <p><?php bloginfo('description'); ?></p>
        </header>
        <main>
            <?php
            if (have_posts()) :
                while (have_posts()) : the_post();
                    the_content();
                endwhile;
            endif;
            ?>
        </main>
    </div>
    <?php wp_footer(); ?>
</body>
</html>
EOF

# Create pages for testing different RSS plugins
echo "Creating test pages for RSS plugins..."

# Page 1: Feedzy RSS Feeds
wp_cli post create \
    --post_type=page \
    --post_title="Amsterdam Events - Feedzy" \
    --post_content='[feedzy-rss feeds="https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml" max="10" feed_title="yes" target="_blank" summary="yes" thumb="yes" size="150" keywords_title="Amsterdam"]' \
    --post_status=publish

# Page 2: WP RSS Aggregator  
wp_cli post create \
    --post_type=page \
    --post_title="Amsterdam Events - WP RSS Aggregator" \
    --post_content='<h2>Amsterdam Events via WP RSS Aggregator</h2><p>This page uses WP RSS Aggregator plugin to display the feed.</p>' \
    --post_status=publish

# Page 3: RSS Import
wp_cli post create \
    --post_type=page \
    --post_title="Amsterdam Events - RSS Import" \
    --post_content='<h2>Amsterdam Events via RSS Import</h2><p>This page uses RSS Import plugin to display the feed.</p>' \
    --post_status=publish

# Page 4: Super RSS Reader
wp_cli post create \
    --post_type=page \
    --post_title="Amsterdam Events - Super RSS Reader" \
    --post_content='[rss-feed url="https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml" max-items="10" show-image="true" show-summary="true"]' \
    --post_status=publish

# Page 5: Custom solution
wp_cli post create \
    --post_type=page \
    --post_title="Amsterdam Events - Custom Display" \
    --post_content='<div id="custom-amsterdam-events">Loading Amsterdam events...</div>

<script>
async function loadAmsterdamEvents() {
    const container = document.getElementById("custom-amsterdam-events");
    
    try {
        const response = await fetch("https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml");
        const xmlText = await response.text();
        
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlText, "text/xml");
        const items = xmlDoc.getElementsByTagName("item");
        
        let html = "<h2>🎭 Amsterdam Events</h2>";
        
        for (let i = 0; i < Math.min(items.length, 10); i++) {
            const item = items[i];
            const title = item.getElementsByTagName("title")[0]?.textContent || "";
            const description = item.getElementsByTagName("description")[0]?.textContent || "";
            const link = item.getElementsByTagName("link")[0]?.textContent || "";
            
            const enclosure = item.getElementsByTagName("enclosure")[0];
            let imageUrl = "";
            if (enclosure) {
                imageUrl = enclosure.getAttribute("url");
            }
            
            html += `
                <div class="event-item">
                    <div class="event-title">${title}</div>
                    ${imageUrl ? `<img src="${imageUrl}" alt="${title}" class="event-image" />` : ""}
                    <div class="event-description">${description}</div>
                    <a href="${link}" class="event-link" target="_blank">View Details →</a>
                </div>
            `;
        }
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = "<p>Error loading events: " + error.message + "</p>";
    }
}

document.addEventListener("DOMContentLoaded", loadAmsterdamEvents);
</script>' \
    --post_status=publish

# Set the homepage to show our content
wp_cli option update show_on_front page
wp_cli option update page_on_front $(wp_cli post list --post_type=page --name="amsterdam-events-feedzy" --field=ID --format=csv)

echo "🎉 WordPress setup complete!"
echo ""
echo "📍 Access URLs:"
echo "   WordPress: http://localhost:8081"
echo "   Admin: http://localhost:8081/wp-admin (admin/admin123)"
echo "   phpMyAdmin: http://localhost:8082"
echo ""
echo "📄 Test Pages Created:"
echo "   - Amsterdam Events - Feedzy"
echo "   - Amsterdam Events - WP RSS Aggregator" 
echo "   - Amsterdam Events - RSS Import"
echo "   - Amsterdam Events - Super RSS Reader"
echo "   - Amsterdam Events - Custom Display"
echo ""
echo "🔧 Plugins Installed:"
echo "   - Feedzy RSS Feeds"
echo "   - WP RSS Aggregator"
echo "   - RSS Import" 
echo "   - Super RSS Reader"
echo "   - Classic Editor"
echo "   - Advanced Custom Fields" 