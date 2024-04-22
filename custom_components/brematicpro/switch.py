import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro switches from a config entry."""
    if entry.entry_id in hass.data[DOMAIN] and hass.data[DOMAIN][entry.entry_id]:
        devices = hass.data[DOMAIN][entry.entry_id]
        entities = [BrematicSwitch(device, hass) for device in devices if device['type'] == 'switch']
        async_add_entities(entities, True)
    else:
        _LOGGER.error("No switch data available for BrematicPro.")


class BrematicSwitch(SwitchEntity):
    """Representation of a BrematicPro Switch."""

    def __init__(self, device_info, hass):
        """Initialize the switch with data from Home Assistant."""
        self._unique_id = device_info['uniqueid']
        self._name = device_info['name']
        self._is_on = False
        self._commands = device_info['commands']
        self._session = async_get_clientsession(hass)

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
        """Return if the switch is turned on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        response = await self._session.post(self._commands['on'])
        if response.status == 200:
            self._is_on = True
        else:
            _LOGGER.error("Failed to turn on: %s", self._name)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        response = await self._session.post(self._commands['off'])
        if response.status == 200:
            self._is_on = False
        else:
            _LOGGER.error("Failed to turn off: %s", self._name)

    async def async_update(self):
        """Fetch new state data for this switch."""
        # This method can optionally be implemented to fetch real-time status.
        pass
