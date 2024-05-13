import logging
from enum import Enum
from homeassistant.core import HomeAssistant
from homeassistant.const import TEMP_CELSIUS, PERCENTAGE
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .BrematicProShared import find_area_id, BrematicProEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    from .BrematicProShared import async_common_setup_entry
    
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProPhoton) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProTemp) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProHumidity)

class BrematicProPhoton(BrematicProEntity, SensorEntity):
    """Representation of a BrematicPro photoluminescence sensor."""
    _type = 'photon'
    _attr_device_class = SensorDeviceClass.ILLUMINANCE

    @property
    def state(self):
        """Return the device state."""
        return self._state

    def update_state(self, device_state):
        self._state = None

class BrematicProTemp(BrematicProEntity, SensorEntity):
    """Representation of a BrematicPro temperature sensor."""
    _type = 'temperature'
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_unit_of_measurement = TEMP_CELSIUS
    _has_battery = True
    #00:00C9:0273 20.1 C  62.7%
    #00:00AD:0362 17.3 C  86.6%

    def __init__(self, hass, coordinator, device, device_entry):
        super().__init__(hass, coordinator, device, device_entry)
        self._state = None

    @property
    def state(self):
        """Return the device state."""
        return self._state

    def update_state(self, device_state):
        self._state = float(int(device_state['state'].split(':')[1], 16)) / 10.0
        self.async_write_ha_state()

class BrematicProHumidity(BrematicProEntity, SensorEntity):
    """Representation of a BrematicPro temperature sensor,  humidity component."""
    _type = 'humidity'
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_unit_of_measurement = PERCENTAGE
    _has_battery = True

    def __init__(self, hass, coordinator, device, device_entry):
        super().__init__(hass, coordinator, device, device_entry)
        self._state = None
        self._unique_id = device['unique_id'] + '.humidity'

    @property
    def state(self):
        """Return the device state."""
        return self._state

    def update_state(self, device_state):
        self._state = float(int(device_state['state'].split(':')[2], 16)) / 10.0
        self.async_write_ha_state()