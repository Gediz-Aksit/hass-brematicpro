import logging
import json
from homeassistant.components.light import LightEntity, COLOR_MODE_ONOFF
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.area_registry import async_get as async_get_area_registry

from .const import DOMAIN, CONF_INTERNAL_JSON
from .readconfigjson import find_area_id, send_command

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro lights from a config entry."""
    
    json_data = entry.data.get(CONF_INTERNAL_JSON)
    if json_data:
        devices = json.loads(json_data)
        entities = []
        existing_entities = {entity.unique_id: entity for entity in hass.data.get(DOMAIN, {}).get(entry.entry_id, [])}
        for device in devices:
            if device['type'] == 'light':
                unique_id = device['uniqueid']
                #area_id = find_area_id(hass, device.get('room'))
                if unique_id in existing_entities:
                    entity = existing_entities[unique_id]
                    entity.update_device(device)
                else:
                    entity = BrematicProLight(device, hass)
                    entities.append(entity)
        async_add_entities(entities, True)
        #hass.data[DOMAIN][entry.entry_id] = list(existing_entities.values()) + entities
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entities
        return True
    return False

class BrematicProLight(BrematicProSwitch, LightEntity):
    """Representation of a Brematic Light."""

    def __init__(self, device, hass):
        """Initialize the light."""
        super().__init__(device, hass)
        self._color_mode = COLOR_MODE_ONOFF
