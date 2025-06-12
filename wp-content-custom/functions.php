<?php
/**
 * Amsterdam Events Theme functions
 */

// Enqueue Tailwind CSS from CDN
function ae_enqueue_styles() {
    wp_enqueue_style(
        'tailwindcss',
        'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css',
        array(),
        null
    );
    wp_enqueue_style(
        'ae-theme-style',
        get_stylesheet_uri(),
        array('tailwindcss'),
        filemtime(get_stylesheet_directory() . '/style.css')
    );
}
add_action('wp_enqueue_scripts', 'ae_enqueue_styles');

// Register shortcode [amsterdam_events]
add_action('init', function () {
    add_shortcode('amsterdam_events', 'ae_render_events_list');
});

/**
 * Render events list from RSS feed.
 *
 * Usage: [amsterdam_events max="12" feed_url="..."]
 */
function ae_render_events_list($atts) {
    // Use the local static feed file in the theme directory for immediate updates
    $atts = shortcode_atts(
        array(
            'max' => 12,
            'feed_url' => get_stylesheet_directory_uri() . '/events.xml',
        ),
        $atts,
        'amsterdam_events'
    );

    if (!function_exists('fetch_feed')) {
        include_once(ABSPATH . WPINC . '/feed.php');
    }
    // Clear cached feed to always fetch the latest version
    delete_transient('feed_' . md5($atts['feed_url']));
    $rss = fetch_feed($atts['feed_url']);
    if (is_wp_error($rss)) {
        return '<p class="text-red-600">Unable to fetch events at this time.</p>';
    }
    $maxitems = $rss->get_item_quantity($atts['max']);
    $items = $rss->get_items(0, $maxitems);
    if (empty($items)) {
        return '<p class="text-gray-500">No events found.</p>';
    }
    $output = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">';
    foreach ($items as $item) {
        // Extract full content of feed item
        $content = $item->get_content();
        // Get first image URL (use enclosure if available, otherwise fallback to content)
        $enclosure = $item->get_enclosure();
        if ($enclosure) {
            $img_url = esc_url($enclosure->get_link());
        } else {
            preg_match('/<img[^>]+src="([^"]+)"/', $content, $m);
            $img_url = isset($m[1]) ? esc_url($m[1]) : '';
        }
        // Get first event date from content block
        if (preg_match('/<span class="event-value">[\s\S]*?<p>(.*?)<\/p>/', $content, $d)) {
            $first_date = esc_html($d[1]);
        } else {
            $first_date = esc_html($item->get_date('j F Y, H:i'));
        }
        // Get description inside event-description-text
        if (preg_match('/<p class="event-description-text">([\s\S]*?)<\/p>/', $content, $md)) {
            $raw_desc = $md[1];
        } else {
            $raw_desc = $item->get_description();
        }
        $desc = wp_trim_words(strip_tags($raw_desc), 15, '...');
        // Compact card output
        $output .= '<div class="bg-white rounded-lg shadow-md overflow-hidden">';
        if ($img_url) {
            $output .= '<img class="w-full h-32 object-cover" src="' . $img_url . '" alt="' . esc_attr($item->get_title()) . '">';
        }
        $output .= '<div class="p-3">';
        $output .= '<h3 class="text-base font-semibold mb-1">' . esc_html($item->get_title()) . '</h3>';
        $output .= '<div class="text-gray-600 text-xs mb-2">' . $first_date . '</div>';
        $output .= '<p class="text-gray-700 text-sm mb-3">' . $desc . '</p>';
        $output .= '<a class="text-blue-600 hover:underline text-xs" href="' . esc_url($item->get_permalink()) . '">View Details</a>';
        $output .= '</div></div>';
    }
    $output .= '</div>';
    return $output;
} 