"""BrematicPro integration for Home Assistant"""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .readconfigjson import read_and_transform_json

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the services for the BrematicPro integration."""

    async def reload_json(call):
        """Service to reload JSON configuration data."""
        for entry in hass.config_entries.async_entries(DOMAIN):
            # Ensure you're calling the read function correctly:
            data = await hass.async_add_executor_job(read_and_transform_json, hass, entry.data)
            if data:
                hass.data[DOMAIN][entry.entry_id] = data
                _LOGGER.info("BrematicPro data reloaded successfully")
            else:
                _LOGGER.error("Failed to reload BrematicPro data")

    hass.services.async_register(DOMAIN, "reload_json", reload_json)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup from a config entry."""
    # Ensure that the data loaded from configuration is set up in hass.data
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    data = await hass.async_add_executor_job(read_and_transform_json, hass, entry.data)
    hass.data[DOMAIN][entry.entry_id] = data

    # Forward the setup to the switch platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, 'switch')
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    # Properly handle the unload and check if it succeeds
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, 'switch')
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
