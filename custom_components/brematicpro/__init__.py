"""BrematicPro integration for Home Assistant"""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, CONF_CONFIG_JSON, CONF_ROOMS_JSON
from .BrematicProShared import read_and_transform_json, setup_entry_components, unload_entry_components, fetch_sensor_states, BrematicProJsonDownloadView

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the BrematicPro component."""
    # Register the HTTP endpoint for downloading JSON data
    view = BrematicProJsonDownloadView()
    hass.http.register_view(view)
    async_track_time_interval(hass, fetch_gateway_states, timedelta(minutes=1))
    return True

async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update a given config entry."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup from a config entry."""
    devices_filename = entry.data.get(CONF_CONFIG_JSON, 'BrematicPro.json')
    rooms_filename = entry.data.get(CONF_ROOMS_JSON, 'BrematicProRooms.json')

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