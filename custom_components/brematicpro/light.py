import logging
from homeassistant.components.light import LightEntity
from .const import DOMAIN
import aiohttp

_LOGGER = logging.getLogger(__name__)

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
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            if response.status == 200:
                self._is_on = True
                self.async_write_ha_state()  # Make sure to update the state in HA
            else:
                _LOGGER.error(f"Failed to turn on the light, status code: {response.status}")
    except Exception as e:
        _LOGGER.error(f"Exception while turning on the light: {e}")

    async def async_turn_off(self, **kwargs):
    """Instruct the light to turn off."""
    url = self._device['commands']['off']
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            if response.status == 200:
                self._is_on = False
                self.async_write_ha_state()  # Update HA state
            else:
                _LOGGER.error(f"Failed to turn off the light, status code: {response.status}")
    except Exception as e:
        _LOGGER.error(f"Exception while turning off the light: {e}")

    async def async_update(self):
        """Fetch new state data for this light."""
        # Here you could check the real-time state, if available from an API
        pass

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up BrematicPro Light from a config entry."""
    devices = get_devices(hass)
    lights = [BrematicProLight(device) for device in devices]
    async_add_entities(lights)
