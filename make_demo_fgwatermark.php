<?php
/**
 * @package     Joomla.Plugin
 * @subpackage  Content.Fgwatermark
 *
 * @copyright   Copyright (C) 2026 FGcodework. All rights reserved.
 * @license     GNU General Public License version 2 or later; see LICENSE.txt
 *
 * Developer tool - NOT part of the installable package.
 *
 * Generates the before/after sample images for the live demo page (docs/)
 * by running the plugin's real Engine (src/Engine.php) on a sample photo.
 * Only the two Joomla classes the Engine touches (Uri, Log) are stubbed, so
 * what you see on the demo page is exactly what the plugin produces.
 *
 * Usage:
 *   php make_demo_fgwatermark.php <photo> [output-dir] [font.ttf]
 *
 *   photo       any JPG/PNG/GIF; resized to 1400px wide first
 *   output-dir  default: docs/images
 *   font.ttf    TTF used for the text-watermark variants (default: first of
 *               a few common bold fonts found on this machine)
 *
 * Writes: original.jpg, logo.jpg, text.jpg, both.jpg
 * Needs:  PHP with the GD extension.
 */

namespace {
	define('_JEXEC', 1);
}

namespace Joomla\CMS\Uri {
	/** Minimal stand-in: the Engine only calls root(true) and getInstance()->getHost(). */
	class Uri
	{
		public static function root($pathOnly = false)
		{
			return '';
		}

		public static function getInstance()
		{
			return new self();
		}

		public function getHost()
		{
			return 'demo.local';
		}
	}
}

namespace Joomla\CMS\Log {
	/** Minimal stand-in: warnings are printed to the console instead. */
	class Log
	{
		const WARNING = 4;

		public static function add($message, $priority = 0, $category = '')
		{
			fwrite(STDERR, "[engine warning] {$message}\n");
		}
	}
}

namespace {
	class DemoParams
	{
		private $data;

		public function __construct(array $data)
		{
			$this->data = $data;
		}

		public function get($key, $default = null)
		{
			return array_key_exists($key, $this->data) ? $this->data[$key] : $default;
		}
	}

	function demoFail($message)
	{
		fwrite(STDERR, $message . "\n");
		exit(1);
	}

	function demoFindFont()
	{
		$candidates = array(
			'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
			'C:\\Windows\\Fonts\\arialbd.ttf',
			'/Library/Fonts/Arial Bold.ttf',
			'/System/Library/Fonts/Supplemental/Arial Bold.ttf',
		);

		foreach ($candidates as $path) {
			if (is_file($path)) {
				return $path;
			}
		}

		return null;
	}

	function demoRemoveDir($dir)
	{
		if (!is_dir($dir)) {
			return;
		}

		foreach (scandir($dir) as $item) {
			if ($item === '.' || $item === '..') {
				continue;
			}

			$path = $dir . '/' . $item;
			is_dir($path) ? demoRemoveDir($path) : unlink($path);
		}

		rmdir($dir);
	}

	$photo  = isset($argv[1]) ? $argv[1] : null;
	$outDir = isset($argv[2]) ? $argv[2] : __DIR__ . '/docs/images';
	$font   = isset($argv[3]) ? $argv[3] : demoFindFont();

	if (!extension_loaded('gd')) {
		demoFail('The GD extension is required.');
	}

	if ($photo === null || !is_file($photo)) {
		demoFail('Usage: php make_demo_fgwatermark.php <photo> [output-dir] [font.ttf]');
	}

	if ($font === null || !is_file($font)) {
		demoFail('No TTF font found - pass one as the third argument.');
	}

	$logo = __DIR__ . '/assets/logo.png';

	if (!is_file($logo)) {
		demoFail('assets/logo.png not found - run this from the repository root.');
	}

	// Throwaway "site root" with just the files the Engine needs to see.
	$root = sys_get_temp_dir() . '/fgwm_demo_' . getmypid();
	mkdir($root . '/images', 0755, true);
	mkdir($root . '/fonts', 0755, true);
	copy($logo, $root . '/images/logo.png');
	copy($font, $root . '/fonts/font.ttf');

	define('JPATH_ROOT', $root);

	require __DIR__ . '/src/Engine.php';

	// Resize the sample photo to a web-friendly width, save it as the "before".
	$source = imagecreatefromstring(file_get_contents($photo));

	if (!$source) {
		demoFail('Could not read the photo.');
	}

	$targetW = 1400;
	$targetH = (int) round(imagesy($source) * ($targetW / imagesx($source)));
	$photoImg = imagecreatetruecolor($targetW, $targetH);
	imagecopyresampled($photoImg, $source, 0, 0, 0, 0, $targetW, $targetH, imagesx($source), imagesy($source));
	imagejpeg($photoImg, $root . '/images/photo.jpg', 88);

	if (!is_dir($outDir)) {
		mkdir($outDir, 0755, true);
	}

	copy($root . '/images/photo.jpg', $outDir . '/original.jpg');

	$common = array(
		'scope_folder'      => 'images/',
		'min_width'         => 150,
		'cache_folder'      => 'images/fgwatermark_cache',
		'cache_expiry'      => 0,
		'jpeg_quality'      => 88,
		'rewrite_links'     => 1,
		'image_enable'      => 0,
		'text_enable'       => 0,
		'image_path'        => 'images/logo.png',
		'image_position'    => 'br',
		'image_margin'      => 28,
		'image_scale'       => 14,
		'image_max_upscale' => 3,
		'image_opacity'     => 90,
		'text_content'      => '© FG Watermark demo',
		'text_font'         => 'fonts/font.ttf',
		'text_size'         => 36,
		'text_color'        => '#0B2338',
		'text_position'     => 'bc',
		'text_margin'       => 28,
		'text_opacity'      => 85,
	);

	$variants = array(
		'logo' => array('image_enable' => 1),
		'text' => array('text_enable' => 1),
		'both' => array('image_enable' => 1, 'text_enable' => 1),
	);

	foreach ($variants as $name => $overrides) {
		$engine = new \FG\Plugin\Content\Fgwatermark\Engine(new DemoParams(array_merge($common, $overrides)));
		$result = $engine->processImgTag('<img src="/images/photo.jpg" alt="">');

		if (!preg_match('/src="([^"]+)"/', $result, $match) || $match[1] === '/images/photo.jpg') {
			demoFail("Variant '{$name}': the Engine did not produce a watermarked copy.");
		}

		$cached = $root . $match[1];

		if (!is_file($cached)) {
			demoFail("Variant '{$name}': expected cache file missing ({$cached}).");
		}

		copy($cached, $outDir . '/' . $name . '.jpg');
	}

	demoRemoveDir($root);

	foreach (array('original', 'logo', 'text', 'both') as $name) {
		$file = $outDir . '/' . $name . '.jpg';
		printf("%-14s %6.1f KB\n", $name . '.jpg', filesize($file) / 1024);
	}
}
