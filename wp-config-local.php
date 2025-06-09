<?php
// WordPress configuration to disable error display for better user experience

// Disable error display on frontend
ini_set('display_errors', 0);
ini_set('display_startup_errors', 0);
error_reporting(0);

// WordPress debug settings
define('WP_DEBUG', false);
define('WP_DEBUG_LOG', false);
define('WP_DEBUG_DISPLAY', false);
@ini_set('display_errors', 0);

// Hide PHP warnings
define('WP_DISABLE_FATAL_ERROR_HANDLER', true); 