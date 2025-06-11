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
            if (is_front_page()) {
    echo '<p><a href="' . esc_url( site_url('?page_id=10&preview=true') ) . '">View the events demo page</a></p>';

                // Shortcode removed; replaced with link above
            } else {
                if (have_posts()) :
                    while (have_posts()) : the_post();
                        the_content();
                    endwhile;
                endif;
            }
            ?>
        </main>
    </div>
    <?php wp_footer(); ?>
</body>
</html>
