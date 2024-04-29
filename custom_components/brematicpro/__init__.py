"""BrematicPro integration for Home Assistant"""
import logging
from datetime import timedelta
import functools

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, CONF_CONFIG_FILE, CONF_ROOMS_FILE
from .BrematicProShared import read_and_transform_json, setup_entry_components, unload_entry_components, fetch_sensor_states, BrematicProJsonDownloadView

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the BrematicPro component."""
    view = BrematicProJsonDownloadView()
    hass.http.register_view(view)
    async_track_time_interval(hass, functools.partial(fetch_sensor_states, hass), timedelta(minutes=1))
    return True

async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update a given config entry."""
    hass.data[DOMAIN][CONF_SYSTEM_CODE] = entry.data.get(CONF_SYSTEM_CODE, "")
    hass.data[DOMAIN][CONF_CONFIG_FILE] = entry.data.get(CONF_CONFIG_FILE, "BrematicPro.json")
    hass.data[DOMAIN][CONF_ROOMS_FILE] = entry.data.get(CONF_ROOMS_FILE, "BrematicProRooms.json")
    hass.data[DOMAIN][CONF_INTERNAL_CONFIG_JSON] = entry.data.get(CONF_INTERNAL_CONFIG_JSON)
    hass.data[DOMAIN][CONF_INTERNAL_GATEWAYS] = entry.data.get(CONF_INTERNAL_GATEWAYS, [])
    hass.data[DOMAIN][CONF_INTERNAL_SENSOR_JSON] = entry.data.get(CONF_INTERNAL_SENSOR_JSON)
    await hass.config_entries.async_reload(entry.entry_id)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup from a config entry."""
    devices_filename = entry.data.get(CONF_CONFIG_FILE, 'BrematicPro.json')
    rooms_filename = entry.data.get(CONF_ROOMS_FILE, 'BrematicProRooms.json')

    # Attempt to read and transform JSON data
    success = await hass.async_add_executor_job(
        read_and_transform_json, hass, entry, devices_filename, rooms_filename
    )

    if not success:
        _LOGGER.error("Failed to load or transform data for BrematicPro")
        return False
    # Setup entry components (switch and light)
    await setup_entry_components(hass, entry)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    _LOGGER.info("Unloading BrematicPro entry.")
    return await unload_entry_components(hass, entry)