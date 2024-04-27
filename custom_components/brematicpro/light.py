import json
import logging
from homeassistant.components.light import LightEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN, CONF_INTERNAL_JSON

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro lights from a config entry."""
    json_data = entry.data.get(CONF_INTERNAL_JSON)
    if json_data:
        devices = json.loads(json_data)
        new_entities = []

        for device in devices:
            if device['type'] == 'light':
                new_entities.append(BrematicProLight(hass, device))

        if new_entities:
            async_add_entities(new_entities, True)

class BrematicProLight(LightEntity):
    """Representation of a Brematic Light."""

    def __init__(self, hass: HomeAssistantType, device):
        """Initialize the light."""
        self._hass = hass
        self._device = device
        self._is_on = False
        self._name = device["name"]
        self._on_command = device["commands"]["on"]
        self._off_command = device["commands"]["off"]
        self._available = True

    @property
    def name(self):
        """Return the name of the light."""
        return self._name

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        await self._send_command(self._on_command)
        self._is_on = True

    async def async_turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        await self._send_command(self._off_command)
        self._is_on = False

    async def async_update(self):
        """Fetch new state data for this light."""
        self._available = True

    async def _send_command(self, url):
        """Send command to the Brematic device using aiohttp."""
        try:
            session = async_get_clientsession(self._hass)
            async with session.get(url) as response:
                response.raise_for_status()
        except Exception as error:
            _LOGGER.error("Error sending command to %s: %s", url, error)
            self._available = False
