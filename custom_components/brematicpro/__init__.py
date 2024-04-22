"""BrematicPro integration for Home Assistant"""
import logging
import json

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_CONFIG_JSON, CONF_ROOMS_JSON, CONF_INTERNAL_JSON
from .readconfigjson import read_and_transform_json

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the services for the BrematicPro integration."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup from a config entry."""
    devices_filename = entry.data.get(CONF_CONFIG_JSON, 'BrematicPro.json')
    rooms_filename = entry.data.get(CONF_ROOMS_JSON, 'BrematicProRooms.json')
    data = await hass.async_add_executor_job(read_and_transform_json, hass, devices_filename, rooms_filename)
    if data:
        json_data = json.dumps(data)
        # Update the entry's data
        hass.config_entries.async_update_entry(entry, data={**entry.data, CONF_INTERNAL_JSON: json_data})
        _LOGGER.debug("Stored BrematicPro configuration data as JSON.")
    else:
        _LOGGER.error("Failed to load or transform data for BrematicPro")
        return False  # Return False to indicate the setup failed

    await hass.config_entries.async_forward_entry_setup(entry, 'switch')
    await hass.config_entries.async_forward_entry_setup(entry, 'light')
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    unload_ok = all([
        await hass.config_entries.async_forward_entry_unload(entry, 'switch'),
        await hass.config_entries.async_forward_entry_unload(entry, 'light')
    ])
    return unload_ok
