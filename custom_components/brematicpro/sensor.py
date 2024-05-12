import logging
from enum import Enum
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .BrematicProShared import find_area_id, BrematicProDevice

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    from .BrematicProShared import async_common_setup_entry
    
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProPhoton) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProTemp) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProHumidity)

class BrematicProPhoton(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro photoluminescence sensor."""
    _type = 'photon'
    _attr_device_class = SensorDeviceClass.ILLUMINANCE

    def update_state(self, device_state):
        self._state = None

class BrematicProTemp(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro temperature sensor."""
    _type = 'temperature'
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _has_battery = True
    #00:00CA:0271
    #00:00AD:0362

    def update_state(self, device_state):
        self._state = None

class BrematicProHumidity(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro temperature sensor,  humidity component."""
    _type = 'humidity'
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _has_battery = True

    def __init__(self, coordinator, device, hass):
        super().__init__(coordinator, device, hass)
        self._commands = []
        self._unique_id = device['unique_id'] + '.humidity'

    def update_state(self, device_state):
        self._state = None