import logging
from enum import Enum
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .BrematicProShared import find_area_id, BrematicProEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    from .BrematicProShared import async_common_setup_entry
    
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProBattery) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProDoor) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProWindow) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProWater) and \
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProMotion)

class BrematicProBattery(BrematicProEntity, BinarySensorEntity):
    """Representation of a BrematicPro device battery status."""
    _type = 'battery'
    _attr_device_class = BinarySensorDeviceClass.BATTERY
    _has_battery = False#A battery does not have its own battery :P
    _attr_is_on = None
    
    def __init__(self, hass, coordinator, device, device_entry):
        """Initialize the battery status indicator."""
        super().__init__(hass, coordinator, device, device_entry)
        self._commands = []
        self._unique_id = device['unique_id'] + '_battery'

    def update_state(self, device_state):
        try:
            if device_state:
                if '1105' == device_state['config']:
                    _LOGGER.debug(f'battery state: full {device_state}; st {device_state['state']}; indx1 {device_state['state'][1]}')
                if device_state['state'][1] == '0':
                    self._attr_is_on  = False
                elif device_state['state'][1] == '3':
                    self._attr_is_on  = True
                elif device_state['state'][1] == '4':
                    self._attr_is_on  = None
                else:
                    self._attr_is_on  = None
            else:
                self._attr_is_on  = None
        except Exception as e:
            _LOGGER.error("Failed to update state: %s", e)
        self.async_write_ha_state()

class BrematicProDoor(BrematicProEntity, BinarySensorEntity):
    """Representation of a BrematicPro door sensor."""
    _type = 'door'
    _attr_device_class = BinarySensorDeviceClass.DOOR
    _has_battery = True
    _attr_is_on = None

    def update_state(self, device_state):
        try:
            #_LOGGER.debug(f"Matching Pair - Entity UID: {self._unique_id}, Name: {self._name}, Device State: {device_state}")
            if device_state['state'][-1] == '7':
                self._attr_is_on  = True
            elif device_state['state'][-1] == '8':
                self._attr_is_on  = False
            else:
                self._attr_is_on  = None
        except Exception as e:
            _LOGGER.error("Failed to update state: %s", e)
        self.async_write_ha_state()

class BrematicProWindow(BrematicProDoor):
    """Representation of a BrematicPro window sensor, inheriting from door sensor."""
    _type = 'window'
    _attr_device_class = BinarySensorDeviceClass.WINDOW

class BrematicProWater(BrematicProEntity, BinarySensorEntity):
    """Representation of a BrematicPro moisture sensor."""
    _type = 'water'
    _attr_device_class = BinarySensorDeviceClass.MOISTURE
    _has_battery = True

    def update_state(self, device_state):
        try:
            if device_state:
                if device_state['state'] == '0001':
                    self._attr_is_on  = True
                elif device_state['state'] == '0002':
                    self._attr_is_on  = False
                else:
                    self._attr_is_on  = None
        except Exception as e:
            _LOGGER.error("Failed to update state: %s", e)

class BrematicProMotion(BrematicProEntity, BinarySensorEntity):
    """Representation of a BrematicPro motion sensor."""
    _type = 'motion'
    _attr_device_class = BinarySensorDeviceClass.MOTION
    _has_battery = True

    def update_state(self, device_state):
        try:
            if device_state:
                if device_state['state'] == '0001':
                    self._attr_is_on  = True
                elif device_state['state'] == '0002':
                    self._attr_is_on  = False
                else:
                    self._attr_is_on  = None
        except Exception as e:
            _LOGGER.error("Failed to update state: %s", e)
