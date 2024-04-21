import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_validation as cv, json as json_util
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro switches from a config entry."""
    file_path = hass.config.path('BrematicProDevices.json')

    # Use Home Assistant's secure method to check if the file path is valid and accessible
    if not hass.config.is_allowed_path(file_path):
        _LOGGER.error("BrematicProDevices.json does not exist or is not accessible at %s", file_path)
        return

    try:
        # Loading JSON using Home Assistant's JSON utility for security and consistency
        devices = json_util.load_json(file_path)
        entities = [BrematicSwitch(device, hass) for device in devices if device['type'] == 'switch']
        async_add_entities(entities, True)
    except json_util.json.JSONDecodeError:
        _LOGGER.error("Error decoding the JSON data in BrematicProDevices.json")
    except Exception as e:
        _LOGGER.error("An error occurred while setting up BrematicPro switches: %s", e)

class BrematicSwitch(SwitchEntity):
    """Representation of a BrematicPro Switch."""

    def __init__(self, device_info, hass):
        """Initialize the switch with data from the JSON file."""
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
        """Return true if the switch is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        url = self._commands['on']
        try:
            response = await self._session.post(url)
            if response.status == 200:
                self._is_on = True
                _LOGGER.info("Successfully turned on %s", self._name)
            else:
                _LOGGER.error("Failed to turn on %s with status: %s", self._name, response.status)
        except Exception as e:
            _LOGGER.error("Error turning on %s: %s", self._name, str(e))

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        url = self._commands['off']
        try:
            response = await self._session.post(url)
            if response.status == 200:
                self._is_on = False
                _LOGGER.info("Successfully turned off %s", self._name)
            else:
                _LOGGER.error("Failed to turn off %s with status: %s", self._name, response.status)
        except Exception as e:
            _LOGGER.error("Error turning off %s: %s", self._name, str(e))

    async def async_update(self):
        """Fetch new state data for this switch."""
        # This method can optionally be implemented to fetch real-time status.
        pass
