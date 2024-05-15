import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.light import LightEntity, ColorMode

from .BrematicProShared import BrematicProEntityWithCommands

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    from .BrematicProShared import async_common_setup_entry
 
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProLight)

class BrematicProLight(BrematicProEntityWithCommands, LightEntity):
    """Representation of a BrematicPro Light."""
    _type = 'light'

    def __init__(self, hass, coordinator, device, device_entry):
        """Initialize the light."""
        super().__init__(hass, coordinator, device, device_entry)
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_supported_color_modes = {ColorMode.ONOFF}

    @property
    def is_on(self):
        """Return the on/off state of the device."""
        if self._frequency == 868:
            return self._is_on
        else:
            return None