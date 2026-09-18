<?php
/**
 * @package     Joomla.Plugin
 * @subpackage  Content.Fgwatermark
 *
 * @copyright   Copyright (C) 2026 FGcodework. All rights reserved.
 * @license     GNU General Public License version 2 or later; see LICENSE.txt
 *
 * Native Joomla 4/5/6 plugin bootstrap. Joomla's plugin loader looks for this
 * exact file (services/provider.php) before falling back to a flat
 * <element>.php file, so no legacy entry point is needed at all - this plugin
 * is native-only (Joomla 4.4+/5/6; Joomla 3.x support ended at v2.x).
 */

defined('_JEXEC') or die;

use FG\Plugin\Content\Fgwatermark\Extension\Fgwatermark;
use Joomla\CMS\Extension\PluginInterface;
use Joomla\CMS\Factory;
use Joomla\CMS\Plugin\PluginHelper;
use Joomla\DI\Container;
use Joomla\DI\ServiceProviderInterface;
use Joomla\Event\DispatcherInterface;

return new class () implements ServiceProviderInterface {
	public function register(Container $container): void
	{
		$container->set(
			PluginInterface::class,
			function (Container $container) {
				$dispatcher = $container->get(DispatcherInterface::class);
				$plugin     = new Fgwatermark(
					$dispatcher,
					(array) PluginHelper::getPlugin('content', 'fgwatermark')
				);
				$plugin->setApplication(Factory::getApplication());

				return $plugin;
			}
		);
	}
};
