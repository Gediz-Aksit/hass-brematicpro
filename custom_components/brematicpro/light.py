import logging
import json

from homeassistant.components.light import LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_INTERNAL_JSON

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro lights from a config entry."""
    json_data = entry.data.get(CONF_INTERNAL_JSON)
    if json_data:
        devices = json.loads(json_data)
        light_devices = [device for device in devices if device['type'] == 'light']
        entities = [BrematicLight(device, hass) for device in light_devices]
        async_add_entities(entities, True)
    else:
        _LOGGER.error("No configuration data found for BrematicPro lights.")

class BrematicLight(LightEntity):
    """Representation of a BrematicPro Light."""

    def __init__(self, device_info, hass):
        """Initialize the light."""
        self._unique_id = device_info['uniqueid']
        self._name = device_info['name']
        self._is_on = False
        self._commands = device_info['commands']
        self._session = async_get_clientsession(hass)

    @property
    def is_on(self):
        """Return if the light is on or off."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        response = await self._session.post(self._commands['on'])
        if response.status == 200:
            self._is_on = True
        else:
            _LOGGER.error("Failed to turn on: %s", self._name)

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        response = await self._session.post(self._commands['off'])
        if response.status == 200:
            self._is_on = False
        else:
            _LOGGER.error("Failed to turn off: %s", self._name)
