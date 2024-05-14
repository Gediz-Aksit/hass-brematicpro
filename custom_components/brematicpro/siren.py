import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.siren import SirenEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .BrematicProShared import send_command#, BrematicProEntity
from .switch import BrematicProSwitch

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up BrematicPro device from a config entry."""
    from .BrematicProShared import async_common_setup_entry
    
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProSiren)

class BrematicProSiren(SirenEntity, BrematicProSwitch):
    """Representation of a Brematic Siren."""
    _type = 'siren'

    def __init__(self, hass, coordinator, device, device_entry):
        """Initialize the siren."""
        super().__init__(hass, coordinator, device, device_entry)
        self._commands = device.get('commands', [])
    
    async def async_turn_reset(self, **kwargs):
        """Instruct the siren reset."""
        response_status = await send_command(self._commands["reset"])
        if response_status == 200:
            self._is_on = False
            self.async_write_ha_state()

    #@property
    #def icon(self):
    #    return "mdi:alarm-light"
