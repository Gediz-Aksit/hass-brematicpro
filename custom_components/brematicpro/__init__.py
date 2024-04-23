"""BrematicPro integration for Home Assistant"""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_CONFIG_JSON, CONF_ROOMS_JSON
from .readconfigjson import read_and_transform_json, setup_entry_components, unload_entry_components, BrematicProJsonDownloadView

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the BrematicPro component."""

    async def download_json_service(call):
        """Service to download the internal JSON."""
        entry_id = call.data.get("entry_id")
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry:
            json_data = entry.data.get("internal_json", "{}")  # Adjust key as needed
            hass.http.register_view(BrematicProJsonDownloadView(json_data))
            _LOGGER.info("JSON download service called.")
        else:
            _LOGGER.error("Entry ID not found.")

    hass.services.async_register(DOMAIN, "download_json", download_json_service)
    return True

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
    return await unload_entry_components(hass, entry)
