import logging
import json
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_INTERNAL_CONFIG_JSON
from .BrematicProShared import find_area_id, send_command, BrematicProEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    from .BrematicProShared import async_common_setup_entry
    
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProSwitch) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProMeteredSwitch)

class BrematicProSwitch(SwitchEntity, BrematicProEntity):
    """Representation of a BrematicPro Switch."""
    _type = 'switch'

    def __init__(self, hass, coordinator, device, device_id):
        """Initialize the switch."""
        super().__init__(hass, coordinator, device, device_id)
        self._is_on = False
        self._commands = device.get('commands', [])

    @property
    def is_on(self):
        """Return the on/off state of the switch."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Instruct the switch on."""
        response_status = await send_command(self._commands["on"])
        if response_status == 200:
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Instruct the switch off."""
        response_status = await send_command(self._commands["off"])
        if response_status == 200:
            self._is_on = False
            self.async_write_ha_state()

    def update_state(self, device_state):
        if device_state['state'] == '0001':
            self._is_on  = True
        elif device_state['state'] == '0002':
            self._is_on  = False
        else:
            self._is_on  = None
        self.async_write_ha_state()

class BrematicProMeteredSwitch(BrematicProSwitch):
    """Representation of a Brematic Metered Switch."""
    _type = 'smartswitch'
    
    def __init__(self, hass, coordinator, device, device_id):
        """Initialize the smart/metered switch."""
        super().__init__(hass, coordinator, device, device_id)
        self._watt = 0.0
        self._voltage = 0.0
        self._kWh = 0.0
        self._Wh = 0.0