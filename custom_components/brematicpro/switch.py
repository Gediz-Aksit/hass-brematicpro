import logging
import json
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import area_registry as ar

from .const import DOMAIN, CONF_INTERNAL_JSON

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro switches from a config entry."""
    json_data = entry.data.get(CONF_INTERNAL_JSON)
    if json_data:
        devices = json.loads(json_data)
        area_registry = await ar.async_get(hass)
        entities = []
        for device in devices:
            if device['type'] == 'switch':
                entity = BrematicSwitch(device, hass, area_registry)
                entities.append(entity)
        async_add_entities(entities, True)
    else:
        _LOGGER.error("No configuration data found for BrematicPro switches.")

class BrematicSwitch(SwitchEntity):
    """Representation of a BrematicPro Switch."""

    def __init__(self, device_info, hass, area_registry):
        """Initialize the switch."""
        self._unique_id = device_info['uniqueid']
        self._name = device_info['name']
        self._is_on = False
        self._commands = device_info['commands']
        self._session = async_get_clientsession(hass)
        self.area_id = self.find_area_id(area_registry, device_info.get('room'))

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
        if response.status == 200:
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        response = await self._session.post(self._commands['off'])
        if response.status == 200:
            self._is_on = False
            self.async_write_ha_state()

    def find_area_id(self, area_registry, room_name):
        """Find area ID by matching room name with area names."""
        if room_name:
            for area in area_registry.areas.values():
                if area.name.lower() == room_name.lower():
                    return area.id
        return None
