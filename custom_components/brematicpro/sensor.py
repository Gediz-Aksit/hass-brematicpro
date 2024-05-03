from homeassistant.components.sensor import SensorEntity

class BrematicProDoor(SensorEntity):
    """Representation of a Brematic Pro Door Sensor."""
    
    def __init__(self, device, hass):
        """Initialize the switch."""
        self._unique_id = device['uniqueid']
        self._name = device['name']
        self._type = device.get('type', None)
        self._frequency =  device.get('freq', None)
        self._suggested_area = device.get('room', None)
        self._is_on = False
        self._session = async_get_clientsession(hass)

    def __init__(self, name, device_id, state):
        self._name = name
        self._device_id = device_id
        self._state = state

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

    @property
    def name(self):
        """Return the name of the window sensor."""
        return f"{self._name} Window"

    async def async_update(self):
        """Update the sensor state specifically for windows."""
        self._state = await self.get_window_state()  # Custom method for window state

# Setup functions to be called from __init__.py
async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up Brematic Pro Door and Window Sensors dynamically."""
    # Device type could be part of the configuration or discovered
    devices = []  # This should be populated based on actual config or discovery
    for device in devices:
        if device['type'] == 'door':
            async_add_devices([BrematicProDoorSensor(device['name'], device['id'], device['initial_state'])])
        elif device['type'] == 'window':
            async_add_devices([BrematicProWindowSensor(device['name'], device['id'], device['initial_state'])])
