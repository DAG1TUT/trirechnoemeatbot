<?php
/**
 * Plugin Name:  AUTOSITE Headless
 * Description:  Кастомные типы записей и REST API для Next.js-фронтенда AUTOSITE.
 *               Устанавливается через «Плагины → Добавить новый → Загрузить плагин».
 * Version:      1.0.0
 * Requires PHP: 8.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// ─── CORS ──────────────────────────────────────────────────────────────────────
// Разрешаем фронтенду (Next.js) читать API.
// URL фронтенда можно задать в Настройки → AUTOSITE.

add_action( 'rest_api_init', function () {
	$origin = get_option( 'autosite_frontend_url', '*' ) ?: '*';
	header( "Access-Control-Allow-Origin: $origin" );
	header( 'Access-Control-Allow-Methods: GET, OPTIONS' );
	header( 'Access-Control-Allow-Credentials: true' );
}, 15 );

// ─── CPT: Автомобиль ───────────────────────────────────────────────────────────

add_action( 'init', function () {

	register_post_type( 'auto', [
		'label'        => 'Автомобили',
		'labels'       => [
			'name'               => 'Автомобили',
			'singular_name'      => 'Автомобиль',
			'add_new_item'       => 'Добавить автомобиль',
			'edit_item'          => 'Редактировать автомобиль',
			'new_item'           => 'Новый автомобиль',
			'view_item'          => 'Смотреть',
			'search_items'       => 'Найти',
			'not_found'          => 'Ничего не найдено',
			'not_found_in_trash' => 'Корзина пуста',
		],
		'public'       => true,
		'show_ui'      => true,
		'show_in_menu' => true,
		'show_in_rest' => true,
		'supports'     => [ 'title', 'thumbnail', 'excerpt' ],
		'menu_icon'    => 'dashicons-car',
		'has_archive'  => false,
		'rewrite'      => false,
	] );

	register_post_type( 'autosite_review', [
		'label'        => 'Отзывы',
		'labels'       => [
			'name'          => 'Отзывы',
			'singular_name' => 'Отзыв',
			'add_new_item'  => 'Добавить отзыв',
			'edit_item'     => 'Редактировать отзыв',
		],
		'public'       => false,
		'show_ui'      => true,
		'show_in_menu' => true,
		'show_in_rest' => true,
		'supports'     => [ 'title', 'editor' ],
		'menu_icon'    => 'dashicons-format-quote',
		'rewrite'      => false,
	] );
} );

// ─── Мета-поля автомобиля ──────────────────────────────────────────────────────

$_autosite_car_meta = [
	'auto_brand'        => [ 'type' => 'string',  'default' => '' ],
	'auto_year'         => [ 'type' => 'integer', 'default' => 0 ],
	'auto_mileage'      => [ 'type' => 'integer', 'default' => 0 ],
	'auto_price'        => [ 'type' => 'integer', 'default' => 0 ],
	'auto_power_hp'     => [ 'type' => 'integer', 'default' => 0 ],
	'auto_transmission' => [ 'type' => 'string',  'default' => '' ],
	'auto_fuel'         => [ 'type' => 'string',  'default' => '' ],
	'auto_body'         => [ 'type' => 'string',  'default' => '' ],
	'auto_color'        => [ 'type' => 'string',  'default' => '' ],
	'auto_is_featured'  => [ 'type' => 'boolean', 'default' => false ],
	'auto_is_new'       => [ 'type' => 'boolean', 'default' => false ],
];

foreach ( $_autosite_car_meta as $key => $cfg ) {
	register_post_meta( 'auto', $key, [
		'show_in_rest' => true,
		'single'       => true,
		'type'         => $cfg['type'],
		'default'      => $cfg['default'],
	] );
}

// ─── Мета-поля отзыва ─────────────────────────────────────────────────────────

foreach ( [ 'review_city', 'review_car_model' ] as $_key ) {
	register_post_meta( 'autosite_review', $_key, [
		'show_in_rest' => true,
		'single'       => true,
		'type'         => 'string',
		'default'      => '',
	] );
}

// ─── REST-роуты ───────────────────────────────────────────────────────────────

add_action( 'rest_api_init', function () {

	// GET /wp-json/autosite/v1/cars[?featured=1&per_page=50]
	register_rest_route( 'autosite/v1', '/cars', [
		'methods'             => 'GET',
		'callback'            => 'autosite_rest_cars',
		'permission_callback' => '__return_true',
		'args'                => [
			'featured' => [ 'type' => 'string',  'default' => '' ],
			'per_page' => [ 'type' => 'integer', 'default' => 50 ],
		],
	] );

	// GET /wp-json/autosite/v1/reviews
	register_rest_route( 'autosite/v1', '/reviews', [
		'methods'             => 'GET',
		'callback'            => 'autosite_rest_reviews',
		'permission_callback' => '__return_true',
	] );

	// GET /wp-json/autosite/v1/settings
	register_rest_route( 'autosite/v1', '/settings', [
		'methods'             => 'GET',
		'callback'            => 'autosite_rest_settings',
		'permission_callback' => '__return_true',
	] );
} );

// ─── Коллбэки роутов ──────────────────────────────────────────────────────────

function autosite_rest_cars( WP_REST_Request $req ): WP_REST_Response {
	$args = [
		'post_type'      => 'auto',
		'post_status'    => 'publish',
		'posts_per_page' => (int) $req->get_param( 'per_page' ),
		'orderby'        => 'date',
		'order'          => 'DESC',
	];

	if ( $req->get_param( 'featured' ) ) {
		$args['meta_query'] = [ [ 'key' => 'auto_is_featured', 'value' => '1' ] ];
	}

	$posts = get_posts( $args );
	return new WP_REST_Response( array_map( 'autosite_format_car', $posts ), 200 );
}

function autosite_format_car( WP_Post $post ): array {
	$thumb = get_the_post_thumbnail_url( $post->ID, 'large' ) ?: '';
	$brand = (string) get_post_meta( $post->ID, 'auto_brand', true );

	return [
		'id'           => (string) $post->ID,
		'name'         => trim( "$brand {$post->post_title}" ),
		'brand'        => $brand,
		'year'         => (int)    get_post_meta( $post->ID, 'auto_year',         true ),
		'mileageKm'    => (int)    get_post_meta( $post->ID, 'auto_mileage',      true ),
		'priceRub'     => (int)    get_post_meta( $post->ID, 'auto_price',        true ),
		'powerHp'      => (int)    get_post_meta( $post->ID, 'auto_power_hp',     true ),
		'transmission' => (string) get_post_meta( $post->ID, 'auto_transmission', true ),
		'fuel'         => (string) get_post_meta( $post->ID, 'auto_fuel',         true ),
		'body'         => (string) get_post_meta( $post->ID, 'auto_body',         true ),
		'color'        => (string) get_post_meta( $post->ID, 'auto_color',        true ),
		'imageSrc'     => $thumb,
		'featured'     => (bool)   get_post_meta( $post->ID, 'auto_is_featured',  true ),
		'new'          => (bool)   get_post_meta( $post->ID, 'auto_is_new',       true ),
	];
}

function autosite_rest_reviews( WP_REST_Request $req ): WP_REST_Response {
	$posts = get_posts( [
		'post_type'      => 'autosite_review',
		'post_status'    => 'publish',
		'posts_per_page' => 20,
		'orderby'        => 'date',
		'order'          => 'DESC',
	] );

	$data = array_map( function ( WP_Post $p ) {
		return [
			'id'   => (string) $p->ID,
			'name' => $p->post_title,
			'city' => (string) get_post_meta( $p->ID, 'review_city',      true ),
			'car'  => (string) get_post_meta( $p->ID, 'review_car_model', true ),
			'text' => wp_strip_all_tags( $p->post_content ),
		];
	}, $posts );

	return new WP_REST_Response( $data, 200 );
}

function autosite_rest_settings( WP_REST_Request $req ): WP_REST_Response {
	return new WP_REST_Response( [
		'phone'   => get_option( 'autosite_phone',   '+7 (999) 000-00-00' ),
		'email'   => get_option( 'autosite_email',   'info@autosite.ru' ),
		'address' => get_option( 'autosite_address', 'Москва, ул. Автомобильная, 1' ),
		'hours'   => get_option( 'autosite_hours',   'Пн–Пт: 9:00–20:00, Сб–Вс: 10:00–18:00' ),
	], 200 );
}

// ─── Страница настроек в WP Admin ─────────────────────────────────────────────

add_action( 'admin_menu', function () {
	add_options_page(
		'AUTOSITE',
		'AUTOSITE',
		'manage_options',
		'autosite-settings',
		'autosite_settings_page'
	);
} );

function autosite_settings_page(): void {
	?>
	<div class="wrap">
		<h1>AUTOSITE — Настройки</h1>
		<form method="post" action="options.php">
			<?php
			settings_fields( 'autosite_settings' );
			do_settings_sections( 'autosite-settings' );
			submit_button( 'Сохранить' );
			?>
		</form>
	</div>
	<?php
}

add_action( 'admin_init', function () {
	add_settings_section( 'autosite_main', 'Контактная информация', '__return_empty_string', 'autosite-settings' );

	$fields = [
		'autosite_phone'        => 'Телефон',
		'autosite_email'        => 'Email',
		'autosite_address'      => 'Адрес',
		'autosite_hours'        => 'Время работы',
		'autosite_frontend_url' => 'URL фронтенда Next.js (для CORS, например http://localhost:3000)',
	];

	foreach ( $fields as $id => $title ) {
		register_setting( 'autosite_settings', $id, [ 'sanitize_callback' => 'sanitize_text_field' ] );
		add_settings_field(
			$id,
			$title,
			static function () use ( $id ) {
				$val = esc_attr( get_option( $id, '' ) );
				echo "<input class='regular-text' type='text' name='{$id}' value='{$val}' />";
			},
			'autosite-settings',
			'autosite_main'
		);
	}
} );
