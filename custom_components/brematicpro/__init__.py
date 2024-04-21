"""BrematicPro integration for Home Assistant"""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the services for the BrematicPro integration."""
    
    async def reload_json(call):
        """Service to reload JSON configuration data."""
        for entry in hass.config_entries.async_entries(DOMAIN):
            data = read_and_transform_json(hass, entry)
            if data:
                hass.data[DOMAIN][entry.entry_id] = data
                _LOGGER.info("BrematicPro data reloaded successfully")
            else:
                _LOGGER.error("Failed to reload BrematicPro data")

    hass.services.async_register(DOMAIN, "reload_json", reload_json)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, 'switch')
    )
	
    hass.config_entries.register_options_flow(
        entry.entry_id, BrematicProOptionsFlow
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "switch")
