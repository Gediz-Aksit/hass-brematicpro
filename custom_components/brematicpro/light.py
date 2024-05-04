from homeassistant.core import HomeAssistant
from homeassistant.components.light import LightEntity, COLOR_MODE_ONOFF

from .BrematicProShared import async_common_setup_entry

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProLight)

class BrematicProLight(BrematicProSwitch, LightEntity):
    """Representation of a Brematic Light."""

    def __init__(self, device, hass):
        """Initialize the light."""
        super().__init__(device, hass)
        self._type = 'light'
        self._color_mode = COLOR_MODE_ONOFF