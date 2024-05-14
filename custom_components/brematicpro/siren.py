import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.siren import SirenEntity

from .switch import BrematicProSwitch
from .BrematicProShared import async_common_setup_entry

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProSiren)

class BrematicProSiren(BrematicProSwitch, SirenEntity):
    """Representation of a Brematic Siren."""
    _type = 'siren'
    
    async def async_turn_reset(self, **kwargs):
        """Instruct the switch reset."""
        response_status = await send_command(self._commands["reset"])
        if response_status == 200:
            self._is_on = False
            self.async_write_ha_state()

    #@property
    #def icon(self):
    #    return "mdi:alarm-light"
