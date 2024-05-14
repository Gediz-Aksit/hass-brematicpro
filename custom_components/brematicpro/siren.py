import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.siren import SirenEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .BrematicProShared import send_command, BrematicProEntity
#from .switch import BrematicProSwitch

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up BrematicPro device from a config entry."""
    from .BrematicProShared import async_common_setup_entry
    
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProSiren)

class BrematicProSiren(SirenEntity, BrematicProEntity):
    """Representation of a Brematic Siren."""
    _type = 'siren'

    def __init__(self, hass, coordinator, device, device_entry):
        """Initialize the siren."""
        super().__init__(hass, coordinator, device, device_entry)
        self._is_on = False
        self._commands = device.get('commands', [])
    
    @property
    def is_on(self):
        """Return the on/off state of the siren."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Instruct the siren on."""
        response_status = await send_command(self._commands["on"])
        if response_status == 200:
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Instruct the siren off."""
        response_status = await send_command(self._commands["off"])
        if response_status == 200:
            self._is_on = False
            self.async_write_ha_state()

    async def async_turn_reset(self, **kwargs):
        """Instruct the siren reset."""
        response_status = await send_command(self._commands["reset"])
        if response_status == 200:
            self._is_on = False
            self.async_write_ha_state()

    #@property
    #def icon(self):
    #    return "mdi:alarm-light"
