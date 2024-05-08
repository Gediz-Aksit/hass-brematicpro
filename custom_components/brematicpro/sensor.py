import logging
from enum import Enum
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .BrematicProShared import async_common_setup_entry, find_area_id, BrematicProDevice

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProLight) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProTemp)

class BrematicProLight(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro photoluminescence sensor."""
    _type = 'light'
    _attr_device_class = SensorDeviceClass.ILLUMINANCE
   
        
class BrematicProTemp(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro temperature sensor."""
    _type = 'temperature'
    _attr_device_class = SensorDeviceClass.TEMPERATURE

