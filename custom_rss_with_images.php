<?php
/**
 * Custom RSS Display with Images
 * A custom WordPress function to display RSS feeds with images included
 */

function display_amsterdam_events_with_images() {
    // Fetch the RSS feed
    $rss_url = 'https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml';
    
    // Try to fetch the RSS content
    $rss_content = wp_remote_get($rss_url);
    
    if (is_wp_error($rss_content)) {
        return '<p>Error: Could not fetch RSS feed</p>';
    }
    
    $body = wp_remote_retrieve_body($rss_content);
    
    // Parse the XML
    $xml = simplexml_load_string($body);
    
    if (!$xml) {
        return '<p>Error: Invalid RSS feed format</p>';
    }
    
    $output = '<div class="amsterdam-events-feed">';
    $output .= '<style>
        .amsterdam-events-feed { max-width: 800px; margin: 0 auto; }
        .event-item { 
            border: 1px solid #ddd; 
            margin: 20px 0; 
            padding: 20px; 
            border-radius: 8px;
            background: #f9f9f9;
        }
        .event-title { 
            color: #E31E24; 
            margin-bottom: 10px; 
            font-size: 1.2em;
            font-weight: bold;
        }
        .event-image { 
            max-width: 300px; 
            height: auto; 
            margin: 10px 0; 
            border-radius: 5px;
            display: block;
        }
        .event-description { 
            line-height: 1.6; 
            color: #555;
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
    </style>';
    
    // Loop through RSS items
    foreach ($xml->channel->item as $item) {
        $title = (string) $item->title;
        $description = (string) $item->description;
        $link = (string) $item->link;
        $pub_date = (string) $item->pubDate;
        
        // Look for enclosure (image)
        $image_url = '';
        if (isset($item->enclosure)) {
            $image_url = (string) $item->enclosure['url'];
        }
        
        $output .= '<div class="event-item">';
        $output .= '<div class="event-title">' . esc_html($title) . '</div>';
        
        // Display image if available
        if (!empty($image_url)) {
            $output .= '<img src="' . esc_url($image_url) . '" alt="' . esc_attr($title) . '" class="event-image" />';
        }
        
        $output .= '<div class="event-description">' . nl2br(esc_html($description)) . '</div>';
        $output .= '<a href="' . esc_url($link) . '" class="event-link" target="_blank">View Details →</a>';
        $output .= '</div>';
    }
    
    $output .= '</div>';
    
    return $output;
}

// Add shortcode support
function amsterdam_events_shortcode($atts) {
    return display_amsterdam_events_with_images();
}
add_shortcode('amsterdam_events', 'amsterdam_events_shortcode');

// Also create a simple test function that can be called directly
if (isset($_GET['test']) && $_GET['test'] === 'amsterdam_events') {
    echo display_amsterdam_events_with_images();
    exit;
}
?> 