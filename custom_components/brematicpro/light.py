import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.light import LightEntity, COLOR_MODE_ONOFF

from .switch import BrematicProSwitch
from .BrematicProShared import async_common_setup_entry

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProLight)

class BrematicProLight(BrematicProSwitch, LightEntity):
    """Representation of a Brematic Light."""
    _type = 'light'

    def __init__(self, device, hass):
        """Initialize the light."""
        super().__init__(device, hass)
        self._color_mode = COLOR_MODE_ONOFF