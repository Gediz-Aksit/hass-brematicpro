import json
import logging
from homeassistant.components.light import LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro light from a config entry."""
    file_path = hass.config.path('BrematicProDevices.json')
    if not os.path.isfile(file_path):
        _LOGGER.error("BrematicProDevices.json does not exist at %s", file_path)
        return

    try:
        with open(file_path, 'r') as file:
            devices = json.load(file)
        entities = [BrematicLight(device, hass) for device in devices if device['type'] == 'light']
        async_add_entities(entities, True)
    except Exception as e:
        _LOGGER.error("An error occurred: %s", e)

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
    def unique_id(self):
        """Return the unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def is_on(self):
        """Return the state."""
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

    async def async_update(self):
        """Fetch new state data for this light."""
        # Here, you could potentially make an API call to check the current state if available
        pass
