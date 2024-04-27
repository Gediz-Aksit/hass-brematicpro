import logging
import json
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_INTERNAL_JSON
from .readconfigjson import find_area_id, send_command

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro switches from a config entry."""
	
    json_data = entry.data.get(CONF_INTERNAL_JSON)
    if json_data:
        devices = json.loads(json_data)
        entities = []
        existing_entities = {entity.unique_id: entity for entity in hass.data.get(DOMAIN, {}).get(entry.entry_id, [])}
        for device in devices:
            if device['type'] == 'switch':
                unique_id = device['uniqueid']
                #area_id = find_area_id(hass, device.get('room'))
                if unique_id in existing_entities:
                    entity = existing_entities[unique_id]
                    entity.update_device(device)
                else:
                    entity = BrematicProSwitch(device, hass)
                    entities.append(entity)
        async_add_entities(entities, True)
        #hass.data[DOMAIN][entry.entry_id] = list(existing_entities.values()) + entities
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entities
        return True
    return False

class BrematicProSwitch(SwitchEntity):
    """Representation of a BrematicPro Switch."""

    def __init__(self, device, hass):
        """Initialize the switch."""
        #self._device = device
        self._unique_id = device['uniqueid']
        self._name = device["name"]
        self._is_on = False
        self._commands = device['commands']
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
        """Return the on/off state of the switch."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Instruct the switch on."""
        response_status = await send_command(self._commands["on"])
        if response_status == 200:
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Instruct the switch off."""
        response_status = await send_command(self._commands["off"])
        if response_status == 200:
            self._is_on = False
            self.async_write_ha_state()

