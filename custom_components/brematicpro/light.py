import json
import logging
import requests
from homeassistant.components.light import LightEntity
from homeassistant.helpers.area_registry import async_get as async_get_area_registry
from .const import DOMAIN, CONF_INTERNAL_JSON
from .readconfigjson import find_area_id

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up BrematicPro lights from a config entry."""
    json_data = entry.data.get(CONF_INTERNAL_JSON)
    if json_data:
        devices = json.loads(json_data)
        entities = []
        new_entities = []
        _LOGGER.warning('Devices ' + json_data)
        existing_entities = {entity.unique_id: entity for entity in hass.data.get(DOMAIN, {}).get(entry.entry_id, [])}
        for device in devices:
            if device['type'] == 'light':
                _LOGGER.warning('Type ' + device['type'])
                unique_id = device['uniqueid']
                _LOGGER.warning('Unique ID ' + unique_id)
                #area_id = find_area_id(hass, device.get('room'))
                if unique_id in existing_entities:
                    _LOGGER.warning('Existing')
                    entity = existing_entities[unique_id]
                    entity.update_device(device)
                else:
                    _LOGGER.warning('New')
                    entity = BrematicProLight(device)
                    entities.append(entity)
        _LOGGER.warning('End of loop')
        async_add_entities(entities, True)
        hass.data[DOMAIN][entry.entry_id] = list(existing_entities.values()) + entities
        return True
    return False

class BrematicProLight(LightEntity):
    """Representation of a Brematic Light."""

    def __init__(self, device):
        """Initialize the light."""
        _LOGGER.warning('Adding ' + device["name"])
        #self._device = device
        self._unique_id = device['uniqueid']
        self._name = device["name"]
        self._is_on = False
        self._commands = device['commands']
        _LOGGER.warning('Added ' + device["name"])

    @property
    def name(self):
        """Return the name of the light."""
        return self._name

    @property
    def is_on(self):
        """Return true if the light is on."""
        return self._is_on

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        self._send_command(self._commands["on"])
        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._send_command(self._commands["off"])
        self._is_on = False
        self.schedule_update_ha_state()

    def _send_command(self, url):
        """Send command to the Brematic device."""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as error:
            _LOGGER.error("Error sending command to %s: %s", url, error)
