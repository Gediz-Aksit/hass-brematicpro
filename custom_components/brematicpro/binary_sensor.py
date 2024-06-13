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

    step1_tasks = [
        async_common_setup_entry(hass, entry, async_add_entities, BrematicProDoor),
        async_common_setup_entry(hass, entry, async_add_entities, BrematicProWindow),
        async_common_setup_entry(hass, entry, async_add_entities, BrematicProWater),
        async_common_setup_entry(hass, entry, async_add_entities, BrematicProMotion)
    ]
    step1_results = await asyncio.gather(*step1_tasks)
    step1_success = all(step1_results)
    if not step1_success:
        _LOGGER.error("Failed to set up primary entities")
        return False
    step2_tasks = [
        async_common_setup_entry(hass, entry, async_add_entities, BrematicProBattery),
        async_common_setup_entry(hass, entry, async_add_entities, BrematicProSabotage)
    ]
    step2_results = await asyncio.gather(*step2_tasks)
    step2_success = all(step2_results)
    if not step2_success:
        _LOGGER.error("Failed to set up secondary entities")
        return False    
    return True

class BrematicProBattery(BrematicProEntity, BinarySensorEntity):
    """Representation of a BrematicPro device battery status."""
    _type = 'battery'
    _attr_device_class = BinarySensorDeviceClass.BATTERY
    _has_battery = False#A battery does not have its own battery :P
    _has_sabotage = False#A batery does not have its own sabotage status
    _attr_is_on = None
    
    def __init__(self, hass, coordinator, device, device_entry):
        """Initialize the battery status indicator."""
        super().__init__(hass, coordinator, device, device_entry)
        self._commands = []
        self._unique_id = device['unique_id'] + '_battery'

    def update_state(self, device_state):
        try:
            if device_state:
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

class BrematicProSabotage(BrematicProEntity, BinarySensorEntity):
    """Representation of a BrematicPro device sabotage status."""
    _type = 'sabotage'
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _has_battery = False#A sabotage status does not have its own battery
    _has_sabotage = False#A sabotage status does not have its own sabotage status :P
    _attr_is_on = None
    
    def __init__(self, hass, coordinator, device, device_entry):
        """Initialize the sabotage status indicator."""
        super().__init__(hass, coordinator, device, device_entry)
        self._commands = []
        self._unique_id = device['unique_id'] + '_sabotage'

    def update_state(self, device_state):
        try:
            if device_state:
                if device_state['state'][1] == '0':
                    self._attr_is_on  = False
                elif device_state['state'][1] == '1':
                    self._attr_is_on  = True
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
    _has_sabotage = True
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
                if device_state['state'][-1] == '1':
                    self._attr_is_on  = True
                elif device_state['state'][-1] == '2':
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
    _has_sabotage = True

    def update_state(self, device_state):
        try:
            if device_state:
                if device_state['state'][-1] == 'D':
                    self._attr_is_on  = True
                elif device_state['state'][-1] == 'E':
                    self._attr_is_on  = False
                else:
                    self._attr_is_on  = None
        except Exception as e:
            _LOGGER.error("Failed to update state: %s", e)
