import asyncio
import logging
from enum import Enum
from homeassistant.core import HomeAssistant
from homeassistant.const import UnitOfTemperature, UnitOfEnergy, UnitOfElectricPotential, UnitOfPower, PERCENTAGE
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .BrematicProShared import find_area_id, BrematicProEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    from .BrematicProShared import async_common_setup_entry

    tasks = [
        async_common_setup_entry(hass, entry, async_add_entities, BrematicProPhoton),
        async_common_setup_entry(hass, entry, async_add_entities, BrematicProTemp),
        async_common_setup_entry(hass, entry, async_add_entities, BrematicProSmartSwitchEnergy),
        async_common_setup_entry(hass, entry, async_add_entities, BrematicProSmartSwitchVoltage),
        async_common_setup_entry(hass, entry, async_add_entities, BrematicProSmartSwitchPower)
    ]
    results = await asyncio.gather(*tasks)
    success = all(results)
    if not success:
        _LOGGER.error("Failed to set up entities")
        return False
    return True

class BrematicProPhoton(BrematicProEntity, SensorEntity):
    """Representation of a BrematicPro photoluminescence sensor."""
    _type = 'photon'
    _attr_device_class = SensorDeviceClass.ILLUMINANCE
    _has_battery = True
    _has_sabotage = True
    _state = None

    @property
    def state(self):
        """Return the device state."""
        return self._state

    def update_state(self, device_state):
        try:
            new_state = int(device_state['state'][-4:], 16)
            if self._state != new_state:
                self._state = new_state
                self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to update state: %s", e)
            if self._state != None:
                self._state = None
                self.async_write_ha_state()

class BrematicProTemp(BrematicProEntity, SensorEntity):
    """Representation of a BrematicPro temperature sensor."""
    _type = 'temperature'
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_unit_of_measurement = UnitOfTemperature.CELSIUS
    _has_battery = True
    _has_sabotage = True
    _state = None
    #00:00C9:0273 20.1 C  62.7%
    #00:00AD:0362 17.3 C  86.6%

    #def __init__(self, hass, coordinator, device, device_entry):
    #    super().__init__(hass, coordinator, device, device_entry)

    @property
    def state(self):
        """Return the device state."""
        return self._state

    def update_state(self, device_state):
        try:
            new_state = float(int(device_state['state'].split(':')[1], 16)) / 10.0
            if self._state != new_state:
                self._state = new_state
                self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to update state: %s", e)
            if self._state != None:
                self._state = None
                self.async_write_ha_state()

class BrematicProHumidity(BrematicProEntity, SensorEntity):
    """Representation of a BrematicPro temperature sensor,  humidity component."""
    _type = 'humidity'
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_unit_of_measurement = PERCENTAGE
    _state = None

    def __init__(self, hass, coordinator, device, device_entry):
        super().__init__(hass, coordinator, device, device_entry)
        self._unique_id = device['unique_id'] + '_' + self._type

    @property
    def state(self):
        """Return the device state."""
        return self._state

    def update_state(self, device_state):
        try:
            new_state = float(int(device_state['state'].split(':')[2], 16)) / 10.0
            if self._state != new_state:
                self._state = new_state
                self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to update state: %s", e)
            if self._state != None:
                self._state = None
                self.async_write_ha_state()

class BrematicProSmartSwitchEnergy(BrematicProEntity, SensorEntity):
    _type = 'smartswitch_energy'
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _state = None
    #000243672F7600000000000F004F
    #                    000F004F Energy in Watt Hours

    def __init__(self, hass, coordinator, device, device_entry):
        super().__init__(hass, coordinator, device, device_entry)
        self._unique_id = device['unique_id'] + '_' + self._type

    @property
    def state(self):
        """Return the device state."""
        return self._state

    def update_state(self, device_state):
        try:
            new_state = new_state = int(device_state['state'].split(':')[0][-8:], 16)
            if self._state != new_state:
                self._state = new_state
                self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to update state: %s", e)
            if self._state != None:
                self._state = None
                self.async_write_ha_state()

class BrematicProSmartSwitchVoltage(BrematicProEntity, SensorEntity):
    _type = 'smartswitch_voltage'
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_unit_of_measurement = UnitOfElectricPotential.VOLT
    _state = None
    #000243672F7600000000000F004F
    #     3672F                   Voltage in volts

    def __init__(self, hass, coordinator, device, device_entry):
        super().__init__(hass, coordinator, device, device_entry)
        self._unique_id = device['unique_id'] + '_' + self._type

    @property
    def state(self):
        """Return the device state."""
        return self._state

    def update_state(self, device_state):
        try:
            new_state = int(device_state['state'].split(':')[0][4:9], 16) / 1000.0
            if self._state != new_state:
                self._state = new_state
                self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to update state: %s", e)
            if self._state != None:
                self._state = None
                self.async_write_ha_state()

class BrematicProSmartSwitchPower(BrematicProEntity, SensorEntity):
    _type = 'smartswitch_power'
    _attr_device_class = SensorDeviceClass.POWER
    _attr_unit_of_measurement = UnitOfPower.WATT
    _state = None
    #000243672F7600000000000F004F
    #                            

    def __init__(self, hass, coordinator, device, device_entry):
        super().__init__(hass, coordinator, device, device_entry)
        self._unique_id = device['unique_id'] + '_' + self._type

    @property
    def state(self):
        """Return the device state."""
        return self._state

    def update_state(self, device_state):
        try:
            new_state = None#new_state = int(device_state['state'].split(':')[0][-8:], 16)
            if self._state != new_state:
                self._state = new_state
                self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to update state: %s", e)
            if self._state != None:
                self._state = None
                self.async_write_ha_state()