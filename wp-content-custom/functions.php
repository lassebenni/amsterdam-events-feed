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
    $atts = shortcode_atts(
        array(
            'max' => 12,
            'feed_url' => 'https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/main/events.xml',
        ),
        $atts,
        'amsterdam_events'
    );

    if (!function_exists('fetch_feed')) {
        include_once(ABSPATH . WPINC . '/feed.php');
    }
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
        $title = esc_html($item->get_title());
        $permalink = esc_url($item->get_permalink());
        $date = esc_html($item->get_date('j F Y, H:i'));
        $description = wp_trim_words($item->get_description(), 20, '...');

        $output .= '<div class="bg-white rounded-lg shadow-lg overflow-hidden">';
        $output .= '<div class="p-4">';
        $output .= "<h2 class=\"text-xl font-semibold mb-2\"><a href=\"{$permalink}\" class=\"text-blue-600 hover:underline\">{$title}</a></h2>";
        $output .= "<p class=\"text-gray-600 text-sm mb-2\">{$date}</p>";
        $output .= "<p class=\"text-gray-700\">{$description}</p>";
        $output .= '</div>';
        $output .= '</div>';
    }
    $output .= '</div>';
    return $output;
} 