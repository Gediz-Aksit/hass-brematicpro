import logging
from homeassistant.components.light import LightEntity
from .const import DOMAIN
import aiohttp

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the light platform."""
    device = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([BrematicProLight(hass, device)])

class BrematicProLight(LightEntity):
    """Representation of a BrematicPro light."""

    def __init__(self, hass, device):
        self.hass = hass
        self._device = device
        self._is_on = False

    @property
    def name(self):
        """Return the display name of this light."""
        return self._device['name']

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        url = self._device['commands']['on']
        _LOGGER.info(f"Turning on the light at {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    self._is_on = True
                _LOGGER.info(f"Light turned on with response {response.status}")

    async def async_turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        url = self._device['commands']['off']
        _LOGGER.info(f"Turning off the light at {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    self._is_on = False
                _LOGGER.info(f"Light turned off with response {response.status}")

    async def async_update(self):
        """Fetch new state data for this light."""
        # Here you could check the real-time state, if available from an API
        pass
