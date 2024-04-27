import requests
import logging
from homeassistant.components.light import LightEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up BrematicPro light based on a config entry."""
    devices = hass.data[DOMAIN].get("devices", [])
    if devices:
        async_add_entities(BrematicProLight(device) for device in devices)

class BrematicProLight(LightEntity):
    """Representation of a Brematic Light."""

    def __init__(self, device):
        """Initialize the light."""
        self._device = device
        self._is_on = False
        self._name = device["name"]
        self._on_command = device["commands"]["on"]
        self._off_command = device["commands"]["off"]

    @property
    def name(self):
        """Return the name of the light."""
        return self._name

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._is_on

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        self._send_command(self._on_command)
        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._send_command(self._off_command)
        self._is_on = False
        self.schedule_update_ha_state()

    def update(self):
        """Fetch new state data for this light."""
        # Here be logic to check the current state of the light if possible
        pass

    def _send_command(self, url):
        """Send command to the Brematic device."""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as error:
            _LOGGER.error("Error sending command to %s: %s", url, error)
