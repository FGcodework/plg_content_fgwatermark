<?php
/**
 * @package     Joomla.Plugin
 * @subpackage  Content.Fgwatermark
 *
 * @copyright   Copyright (C) 2026 FGcodework. All rights reserved.
 * @license     GNU General Public License version 2 or later; see LICENSE.txt
 *
 * Native Joomla 4/5/6 plugin class, wired up via services/provider.php.
 * Thin wrapper: all real work happens in Engine (src/Engine.php).
 */

namespace FG\Plugin\Content\Fgwatermark\Extension;

use FG\Plugin\Content\Fgwatermark\Engine;
use Joomla\CMS\Plugin\CMSPlugin;
use Joomla\Event\Event;
use Joomla\Event\SubscriberInterface;

defined('_JEXEC') or die;

final class Fgwatermark extends CMSPlugin implements SubscriberInterface
{
	protected $autoloadLanguage = true;

	/** @var Engine|null */
	private $engine;

	/**
	 * @return array<string, string>
	 */
	public static function getSubscribedEvents(): array
	{
		return [
			'onContentPrepare' => 'onContentPrepare',
		];
	}

	public function onContentPrepare(Event $event): void
	{
		$imageEnabled = (int) $this->params->get('image_enable', 0);
		$textEnabled  = (int) $this->params->get('text_enable', 0);

		if (!$imageEnabled && !$textEnabled) {
			return;
		}

		// Positional destructure (context, item, params, page) - robust against
		// whether Joomla passed a generic Event or a concrete ContentPrepareEvent,
		// since the legacy argument order is preserved either way.
		$values = array_values($event->getArguments());
		$row    = $values[1] ?? null;

		if (!is_object($row)) {
			return;
		}

		if ($this->engine === null) {
			$this->engine = new Engine($this->params);
		}

		if (isset($row->text)) {
			$row->text = $this->engine->processHtml($row->text);
		} elseif (isset($row->introtext)) {
			$row->introtext = $this->engine->processHtml($row->introtext);

			if (isset($row->fulltext)) {
				$row->fulltext = $this->engine->processHtml($row->fulltext);
			}
		}
	}
}
