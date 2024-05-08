import logging
from enum import Enum
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .BrematicProShared import async_common_setup_entry, find_area_id, BrematicProDevice

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProDoor) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProWindow) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProWater) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProMotion) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProLight) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProTemp)

class ContactState(Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    UNKNOWN = 'unknown'

class BrematicProDoor(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro door sensor."""
    _type = 'door'
    _attr_is_on = None
    _attr_device_class = BinarySensorDeviceClass.DOOR

    def update_state(self, device_state):
        if device_state:
            if device_state['state'] == '0001':
                self._attr_is_on  = True
            else if device_state['state'] == '0002':
                self._attr_is_on  = False
            else:
                self._attr_is_on  = None

class BrematicProWindow(BrematicProDoor):
    """Representation of a BrematicPro window sensor, inheriting from door sensor."""
    _type = 'window'
    _attr_device_class = BinarySensorDeviceClass.WINDOW

class BrematicProWater(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro moisture sensor."""
    _type = 'water'
    _attr_device_class = BinarySensorDeviceClass.MOISTURE

class BrematicProMotion(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro motion sensor."""
    _type = 'motion'
    _attr_device_class = BinarySensorDeviceClass.MOTION

class BrematicProLight(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro photoluminescence sensor."""
    _type = 'light'
    _attr_device_class = SensorDeviceClass.ILLUMINANCE
   
        
class BrematicProTemp(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro temperature sensor."""
    _type = 'temperature'
    _attr_device_class = SensorDeviceClass.TEMPERATURE

