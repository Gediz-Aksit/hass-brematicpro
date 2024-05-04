from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .door import BrematicProDoor
from .BrematicProShared import async_common_setup_entry

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProWindow)

class BrematicProWindow(BrematicProDoor):
    """Representation of a Brematic Pro Window Sensor, inheriting from Door Sensor."""
    
    _type = 'window'
    
    def __init__(self, device, hass):
        """Initialize the light."""
        super().__init__(device, hass)
        self._type = 'window'
    @property
    def name(self):
        """Return the name of the window sensor."""
        return f"{self._name} Window"

    async def async_update(self):
        """Update the sensor state specifically for windows."""
        self._state = await self.get_window_state()  # Custom method for window state
