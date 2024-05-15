import logging
import json
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_INTERNAL_CONFIG_JSON
from .BrematicProShared import send_command, BrematicProEntityWithCommands

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    from .BrematicProShared import async_common_setup_entry
    
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProSwitch) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProMeteredSwitch)

class BrematicProSwitch(SwitchEntity, BrematicProEntityWithCommands):
    """Representation of a BrematicPro Switch."""
    _type = 'switch'

    @property
    def is_on(self):
        """Return the on/off state of the device."""
        if self._frequency == 868:
            return self._is_on
        else:
            return None

    def update_state(self, device_state):
        try:
            if device_state['state'][-1] == '1':
                self._is_on  = True
            elif device_state['state'][-1] == '2':
                self._is_on  = False
            else:
                self._is_on  = None
        except Exception as e:
            _LOGGER.error("Failed to update state: %s", e)
        self.async_write_ha_state()

class BrematicProMeteredSwitch(BrematicProSwitch):
    """Representation of a Brematic Metered Switch."""
    _type = 'smartswitch'
    
    def __init__(self, hass, coordinator, device, device_entry):
        """Initialize the smart/metered switch."""
        super().__init__(hass, coordinator, device, device_entry)
        self._watt = 0.0
        self._voltage = 0.0
        self._kWh = 0.0
        self._Wh = 0.0

    def update_state(self, device_state):

        super().update_state(device_state)
