"""BrematicPro integration for Home Assistant"""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_CONFIG_JSON, CONF_ROOMS_JSON
from .readconfigjson import read_and_transform_json

_LOGGER = logging.getLogger(__name__)

def ensure_domain_dict(hass, domain):
    """Ensure the domain key in hass.data is a dict."""
    if domain not in hass.data:
        hass.data[domain] = {}
    elif not isinstance(hass.data[domain], dict):
        _LOGGER.error(f"Expected hass.data['{domain}'] to be a dict but found {type(hass.data[domain])}")
        hass.data[domain] = {}  # Reset to dict if it's not

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the services for the BrematicPro integration."""
    ensure_domain_dict(hass, DOMAIN)

    async def reload_json(call):
        """Service to reload JSON configuration data."""
        ensure_domain_dict(hass, DOMAIN)
        for entry in hass.config_entries.async_entries(DOMAIN):
            devices_filename = entry.data.get(CONF_CONFIG_JSON, 'BrematicPro.json')
            rooms_filename = entry.data.get(CONF_ROOMS_JSON, 'BrematicProRooms.json')
            data = await hass.async_add_executor_job(read_and_transform_json, hass, devices_filename, rooms_filename)
            if data:
                hass.data[DOMAIN][entry.entry_id] = data
                _LOGGER.info("BrematicPro data reloaded successfully")
            else:
                _LOGGER.error("Failed to reload BrematicPro data")

    hass.services.async_register(DOMAIN, "reload_json", reload_json)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup from a config entry."""
    ensure_domain_dict(hass, DOMAIN)

    devices_filename = entry.data.get(CONF_CONFIG_JSON, 'BrematicPro.json')
    rooms_filename = entry.data.get(CONF_ROOMS_JSON, 'BrematicProRooms.json')
    data = await hass.async_add_executor_job(read_and_transform_json, hass, devices_filename, rooms_filename)
    if data:
        hass.data[DOMAIN][entry.entry_id] = data
        _LOGGER.debug("Loaded data for BrematicPro: %s", data)
    else:
        _LOGGER.error("Failed to load or transform data for BrematicPro")
        return False  # Return False to indicate the setup failed

    #await hass.config_entries.async_forward_entry_setup(entry, 'switch')
    #await hass.config_entries.async_forward_entry_setup(entry, 'light')
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    ensure_domain_dict(hass, DOMAIN)
    unload_ok = all([
        await hass.config_entries.async_forward_entry_unload(entry, 'switch'),
        await hass.config_entries.async_forward_entry_unload(entry, 'light')
    ])
    if unload_ok:
        if entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
