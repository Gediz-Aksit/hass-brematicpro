import logging
import json
from homeassistant.components.light import LightEntity, COLOR_MODE_ONOFF
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.area_registry import async_get as async_get_area_registry

from .const import DOMAIN, CONF_INTERNAL_JSON
from .readconfigjson import async_common_setup_entry
from .switch import BrematicProSwitch

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro lights from a config entry."""
    return await async_common_setup_entry(hass, entry, async_add_entities, 'light', BrematicProLight)

class BrematicProLight(BrematicProSwitch, LightEntity):
    """Representation of a Brematic Light."""

    def __init__(self, device, hass):
        """Initialize the light."""
        super().__init__(device, hass)
        self._color_mode = COLOR_MODE_ONOFF
