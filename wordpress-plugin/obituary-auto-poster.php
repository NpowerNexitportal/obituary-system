<?php
/**
 * Plugin Name: Obituary Auto Poster
 * Description: Automatically fetches and publishes obituaries from the Obituary Content API via Webhook.
 * Version: 1.1
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
        __('API & Webhook Configuration', 'wordpress'), 
        'oap_settings_section_callback', 
        'pluginPage'
    );

    add_settings_field(
        'oap_api_url', 
        __('FastAPI URL', 'wordpress'), 
        'oap_api_url_render', 
        'pluginPage', 
        'oap_pluginPage_section'
    );

    add_settings_field(
        'oap_webhook_secret', 
        __('Webhook Secret', 'wordpress'), 
        'oap_webhook_secret_render', 
        'pluginPage', 
        'oap_pluginPage_section'
    );
}

function oap_api_url_render() {
    $options = get_option('oap_settings');
    ?>
    <input type='url' name='oap_settings[oap_api_url]' value='<?php echo isset($options['oap_api_url']) ? esc_attr($options['oap_api_url']) : ''; ?>' style="width: 400px;" placeholder="https://obituary-api-iy8w.onrender.com/api/obituaries">
    <?php
}

function oap_webhook_secret_render() {
    $options = get_option('oap_settings');
    ?>
    <input type='text' name='oap_settings[oap_webhook_secret]' value='<?php echo isset($options['oap_webhook_secret']) ? esc_attr($options['oap_webhook_secret']) : wp_generate_password(12, false); ?>' style="width: 400px;">
    <p class="description">Required to securely trigger the fetch externally.</p>
    <?php
}

function oap_settings_section_callback() {
    $options = get_option('oap_settings');
    $secret = isset($options['oap_webhook_secret']) ? $options['oap_webhook_secret'] : 'YOUR_SECRET';
    $webhook_url = site_url("/wp-json/obituary/v1/fetch?secret={$secret}");
    
    echo __('Configure your API source and your secure Webhook.', 'wordpress');
    echo '<br><br><strong>Your Webhook Trigger URL:</strong><br>';
    echo '<code>' . esc_url($webhook_url) . '</code>';
    echo '<p>You can ping this URL from GitHub Actions, Cron-job.org, or any external service to securely trigger a fetch!</p>';
}

function oap_options_page() {
    ?>
    <form action='options.php' method='post'>
        <h2>Obituary Auto Poster (Webhook Edition)</h2>
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

// 4. REST API Webhook Setup (Replaces WP-Cron)
add_action('rest_api_init', function () {
    register_rest_route('obituary/v1', '/fetch', array(
        'methods' => 'GET',
        'callback' => 'oap_webhook_fetch_handler',
        'permission_callback' => '__return_true'
    ));
});

function oap_webhook_fetch_handler(WP_REST_Request $request) {
    $secret = $request->get_param('secret');
    $options = get_option('oap_settings');
    $stored_secret = isset($options['oap_webhook_secret']) ? $options['oap_webhook_secret'] : '';
    
    if (empty($stored_secret) || $secret !== $stored_secret) {
        return new WP_Error('rest_forbidden', esc_html__('Invalid or missing Secret Key.', 'wordpress'), array('status' => 401));
    }
    
    $count = oap_fetch_and_publish();
    return rest_ensure_response(array(
        'status' => 'success', 
        'message' => 'Obituaries fetched successfully.',
        'processed' => $count
    ));
}

// Ensure Category Exists on Activation
register_activation_hook(__FILE__, 'oap_activation');
function oap_activation() {
    if (!term_exists('Obituaries', 'category')) {
        wp_insert_term('Obituaries', 'category');
    }
}

// 5. Fetch and Publish Logic
function oap_fetch_and_publish() {
    $options = get_option('oap_settings');
    $api_url = isset($options['oap_api_url']) ? $options['oap_api_url'] : '';

    if (empty($api_url)) {
        return 0;
    }

    $response = wp_remote_get($api_url, array('timeout' => 15));

    if (is_wp_error($response)) {
        error_log('OAP Error: Failed to fetch API - ' . $response->get_error_message());
        return 0;
    }

    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);

    if (empty($data) || !isset($data['data']) || !is_array($data['data'])) {
        return 0;
    }

    $category_id = get_cat_ID('Obituaries');
    $inserted_count = 0;

    foreach ($data['data'] as $obituary) {
        $slug = sanitize_title($obituary['slug']);
        
        // Check if post exists by slug to avoid duplicates
        $existing_post = get_page_by_path($slug, OBJECT, 'post');
        
        if (!$existing_post) {
            // Create post
            $post_data = array(
                'post_title'    => wp_strip_all_tags($obituary['title']),
                'post_name'     => $slug,
                'post_content'  => wp_kses_post($obituary['content']),
                'post_status'   => 'publish',
                'post_author'   => 1,
                'post_category' => array($category_id)
            );

            $post_id = wp_insert_post($post_data);

            if (!is_wp_error($post_id)) {
                // Add Meta Description for SEO plugins like Yoast or RankMath
                update_post_meta($post_id, '_yoast_wpseo_metadesc', sanitize_text_field($obituary['meta_description']));
                update_post_meta($post_id, 'rank_math_description', sanitize_text_field($obituary['meta_description']));
                $inserted_count++;
            }
        }
    }
    
    return $inserted_count;
}
?>
