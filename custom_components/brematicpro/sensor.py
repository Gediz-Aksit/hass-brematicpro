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
           await async_common_setup_entry(hass, entry, async_add_entities, BrematicProTemp)

class ContactState(Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    UNKNOWN = 'unknown'

class BrematicProDoor(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro door sensor."""
    _type = 'door'
    
    def __init__(self, device, hass):
        """Initialize the door sensor."""
        super().__init__(device, hass)
        self._contact_state = ContactState.UNKNOWN

    @property
    def state(self):
        """Return the current state of the door sensor."""
        return self._contact_state.value

class BrematicProWindow(BrematicProDoor):
    """Representation of a BrematicPro window sensor, inheriting from door sensor."""
    _type = 'window'
    
    def __init__(self, device, hass):
        """Initialize the window."""
        super().__init__(device, hass)

class BrematicProWater(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro water sensor."""
    _type = 'water'
    
    def __init__(self, device, hass):
        """Initialize the window."""
        super().__init__(device, hass)

class BrematicProMotion(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro motion sensor."""
    _type = 'motion'
    
    def __init__(self, device, hass):
        """Initialize the window."""
        super().__init__(device, hass)
        
class BrematicProTemp(BrematicProDevice, SensorEntity):
    """Representation of a BrematicPro temperature sensor."""
    _type = 'temperature'
    
    def __init__(self, device, hass):
        """Initialize the window."""
        super().__init__(device, hass)
