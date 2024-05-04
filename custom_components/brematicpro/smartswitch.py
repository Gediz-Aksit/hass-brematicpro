import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


from .switch import BrematicProSwitch
from .BrematicProShared import async_common_setup_entry

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProMeteredSwitch)

class BrematicProMeteredSwitch(BrematicProSwitch):
    """Representation of a Brematic Metered Switch."""
    _type = 'smartswitch'
    
    def __init__(self, device, hass):
        """Initialize the smart/metered switch."""
        super().__init__(device, hass)
        self._watt = 0.0
        self._voltage = 0.0
        self._kWh = 0.0
        self._Wh = 0.0