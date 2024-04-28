import asyncio
import logging
from datetime import timedelta
import aiohttp
import json

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)  # How often to poll the device, set to once a minute

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform."""
    coordinator = BrematicDataCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([BrematicSensor(coordinator)], True)

class BrematicDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the device."""

    def __init__(self, hass):
        """Initialize."""
        self.hass = hass
        self.api_url = "http://192.168.0.26/cmd?XC_FNC=SendSC&type=B4&at=YOUR_SYSTEM_CODE&data=getStates"
        super().__init__(hass, _LOGGER, name="BrematicSensor", update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Fetch data from BrematicGateway."""
        try:
            async with async_get_clientsession(self.hass).get(self.api_url) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching data: {response.status}")
                json_data = await response.json()
                return json_data
        except Exception as e:
            raise UpdateFailed(f"Error communicating with API: {str(e)}")

class BrematicSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Brematic State"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data

    @property
    def available(self):
        """Return if sensor is available."""
        return self.coordinator.last_update_success

    async def async_update(self):
        """Update Brematic sensor."""
        await self.coordinator.async_request_refresh()
