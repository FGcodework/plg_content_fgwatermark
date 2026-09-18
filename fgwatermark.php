<?php
/**
 * @package     Joomla.Plugin
 * @subpackage  Content.Fgwatermark
 *
 * @copyright   Copyright (C) 2026 FGcodework. All rights reserved.
 * @license     GNU General Public License version 2 or later; see LICENSE.txt
 *
 * Entry point. Joomla's plugin loader always includes this exact file and then
 * looks for a class called PlgContentFgwatermark - regardless of Joomla version.
 * What differs across versions is HOW that class needs to be built:
 *
 *  - Joomla 3.x: classic JPlugin, events auto-attached by method name.
 *  - Joomla 4/5/6: Joomla\Event\SubscriberInterface, explicit getSubscribedEvents().
 *    (CMSPlugin's legacy on*-method auto-registration is removed as of 6.0,
 *    so this path is required from 6.0 onward, and works fine on 4/5 too.)
 *
 * Only one of the two files below is ever require'd, so only one
 * PlgContentFgwatermark class definition is ever declared - no conflict.
 */

defined('_JEXEC') or die;

require_once __DIR__ . '/src/engine.php';

if (interface_exists('Joomla\\Event\\SubscriberInterface')) {
	require_once __DIR__ . '/src/modern.php';
} else {
	require_once __DIR__ . '/src/legacy.php';
}
