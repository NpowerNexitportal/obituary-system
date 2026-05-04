<?php
/**
 * Plugin Name: Obituary Auto Poster
 * Description: Automatically fetches and publishes obituaries from the Obituary Content API.
 * Version: 1.0
 * Author: AutoPost
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly.
}

// 1. Add Settings Menu
add_action('admin_menu', 'oap_add_admin_menu');
function oap_add_admin_menu() {
    add_options_page('Obituary Auto Poster', 'Obituary Poster', 'manage_options', 'obituary-auto-poster', 'oap_options_page');
}

// 2. Register Settings
add_action('admin_init', 'oap_settings_init');
function oap_settings_init() {
    register_setting('pluginPage', 'oap_settings');

    add_settings_section(
        'oap_pluginPage_section', 
        __('API Configuration', 'wordpress'), 
        'oap_settings_section_callback', 
        'pluginPage'
    );

    add_settings_field(
        'oap_api_url', 
        __('API URL', 'wordpress'), 
        'oap_api_url_render', 
        'pluginPage', 
        'oap_pluginPage_section'
    );
}

function oap_api_url_render() {
    $options = get_option('oap_settings');
    ?>
    <input type='url' name='oap_settings[oap_api_url]' value='<?php echo isset($options['oap_api_url']) ? esc_attr($options['oap_api_url']) : ''; ?>' style="width: 400px;" placeholder="https://your-fastapi-url.com/api/obituaries">
    <?php
}

function oap_settings_section_callback() {
    echo __('Enter the endpoint URL for your Obituary FastAPI server.', 'wordpress');
}

function oap_options_page() {
    ?>
    <form action='options.php' method='post'>
        <h2>Obituary Auto Poster</h2>
        <?php
        settings_fields('pluginPage');
        do_settings_sections('pluginPage');
        submit_button();
        ?>
    </form>
    <form action="<?php echo admin_url('admin-post.php'); ?>" method="post">
        <input type="hidden" name="action" value="oap_manual_fetch">
        <?php submit_button('Fetch Now (Manual Run)', 'secondary'); ?>
    </form>
    <?php
}

// 3. Handle Manual Fetch
add_action('admin_post_oap_manual_fetch', 'oap_manual_fetch_handler');
function oap_manual_fetch_handler() {
    if (!current_user_can('manage_options')) {
        wp_die('Unauthorized');
    }
    oap_fetch_and_publish();
    wp_redirect(admin_url('options-general.php?page=obituary-auto-poster&fetched=true'));
    exit;
}

// 4. CRON Setup
register_activation_hook(__FILE__, 'oap_activation');
function oap_activation() {
    if (!wp_next_scheduled('oap_hourly_event')) {
        wp_schedule_event(time(), 'hourly', 'oap_hourly_event'); // Run hourly
    }
    
    // Ensure category exists
    if (!term_exists('Obituaries', 'category')) {
        wp_insert_term('Obituaries', 'category');
    }
}

register_deactivation_hook(__FILE__, 'oap_deactivation');
function oap_deactivation() {
    wp_clear_scheduled_hook('oap_hourly_event');
}

add_action('oap_hourly_event', 'oap_fetch_and_publish');

// 5. Fetch and Publish Logic
function oap_fetch_and_publish() {
    $options = get_option('oap_settings');
    $api_url = isset($options['oap_api_url']) ? $options['oap_api_url'] : '';

    if (empty($api_url)) {
        return;
    }

    $response = wp_remote_get($api_url, array('timeout' => 15));

    if (is_wp_error($response)) {
        error_log('OAP Error: Failed to fetch API - ' . $response->get_error_message());
        return;
    }

    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);

    if (empty($data) || !isset($data['data']) || !is_array($data['data'])) {
        return;
    }

    $category_id = get_cat_ID('Obituaries');

    foreach ($data['data'] as $obituary) {
        $slug = sanitize_title($obituary['slug']);
        
        // Check if post exists by slug to avoid duplicates
        $existing_post = get_page_by_path($slug, OBJECT, 'post');
        
        if (!$existing_post) {
            // Create post
            $post_data = array(
                'post_title'    => wp_strip_all_tags($obituary['title']),
                'post_name'     => $slug,
                'post_content'  => $obituary['content'] . "\n\n<br><em>Source: " . esc_url($obituary['source_url']) . "</em>",
                'post_status'   => 'publish',
                'post_author'   => 1,
                'post_category' => array($category_id)
            );

            $post_id = wp_insert_post($post_data);

            if (!is_wp_error($post_id)) {
                // Add Meta Description for SEO plugins like Yoast or RankMath
                update_post_meta($post_id, '_yoast_wpseo_metadesc', sanitize_text_field($obituary['meta_description']));
                update_post_meta($post_id, 'rank_math_description', sanitize_text_field($obituary['meta_description']));
            }
        }
    }
}
?>
