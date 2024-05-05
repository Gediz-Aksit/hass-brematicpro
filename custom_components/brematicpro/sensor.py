import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .BrematicProShared import async_common_setup_entry, find_area_id

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrematicPro device from a config entry."""
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProDoor) and \
                 async_common_setup_entry(hass, entry, async_add_entities, BrematicProWindow)

class BrematicProDoor(SensorEntity):
    """Representation of a Brematic Pro Door Sensor."""
    _type = 'door'
    
    def __init__(self, device, hass):
        """Initialize the switch."""
        self._unique_id = device['uniqueid']
        self._name = device['name']
        self._frequency =  device.get('freq', None)
        self._suggested_area = device.get('room', None)
        self._is_on = False
        self._session = async_get_clientsession(hass)
        #self._state = state

    @property
    def name(self):
        """Return the name of the door sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the door is open."""
        return self._state == 'open'

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._device_id

    async def async_update(self):
        """Update the sensor state."""
        self._state = await self.get_state()  # Assume this method gets the current state

class BrematicProWindow(BrematicProDoor):
    """Representation of a Brematic Pro Window Sensor, inheriting from Door Sensor."""
    
    _type = 'window'
    
    def __init__(self, device, hass):
        """Initialize the light."""
        super().__init__(device, hass)

    @property
    def name(self):
        """Return the name of the window sensor."""
        return f"{self._name} Window"

    async def async_update(self):
        """Update the sensor state specifically for windows."""
        self._state = await self.get_window_state()  # Custom method for window state