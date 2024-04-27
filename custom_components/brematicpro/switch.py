import logging
import json
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_INTERNAL_JSON
from .readconfigjson import find_area_id  # Ensure correct import

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro switches from a config entry."""
    # Prevent setup from running more than once per entry
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        return False

    json_data = entry.data.get(CONF_INTERNAL_JSON)
    if json_data:
        devices = json.loads(json_data)
        entities = []
        for device in devices:
            if device['type'] == 'switch':
                entity = BrematicSwitch(device, hass)
                entities.append(entity)
        async_add_entities(entities, True)
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entities
        return True
    else:
        _LOGGER.error("No configuration data found for BrematicPro switches.")
        return False

class BrematicSwitch(SwitchEntity):
    """Representation of a BrematicPro Switch."""

    def __init__(self, device_info, hass):
        """Initialize the switch."""
        self._unique_id = device_info['uniqueid']
        self._name = device_info['name']
        self._is_on = False
        self._commands = device_info['commands']
        self._session = async_get_clientsession(hass)
        self.area_id = find_area_id(hass, device_info.get('room'))

    @property
    def unique_id(self):
        """Return the unique ID of the switch."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return the on/off state of the switch."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        response = await self._session.post(self._commands['on'])
        _LOGGER.info(f"Turn on response: {response.status} - {await response.text()}")
        if response.status == 200:
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        response = await self._session.post(self._commands['off'])
        _LOGGER.info(f"Turn off response: {response.status} - {await response.text()}")
        if response.status == 200:
            self._is_on = False
            self.async_write_ha_state()
