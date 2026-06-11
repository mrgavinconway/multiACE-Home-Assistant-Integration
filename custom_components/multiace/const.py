"""Constants for the multiACE integration."""

from __future__ import annotations

from logging import Logger, getLogger

DOMAIN = "multiace"
LOGGER: Logger = getLogger(__package__)

CONF_BASE_URL = "base_url"
CONF_DRYER_TEMP = "dryer_temp"
CONF_DRYER_DURATION = "dryer_duration"

DEFAULT_BASE_URL = "http://yourprinter/multiace/"
DEFAULT_DRYER_TEMP = 50
DEFAULT_DRYER_DURATION = 240

MAX_ACE_COUNT = 4
SLOT_COUNT = 4
SCAN_INTERVAL_SECONDS = 15

ATTR_ACE = "ace"
ATTR_SLOT = "slot"
