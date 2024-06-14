"""BrematicPro integration for Home Assistant"""
import logging
from datetime import timedelta
import functools
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_CONFIG_FILE, CONF_ROOMS_FILE, CONF_INTERNAL_GATEWAYS
from .BrematicProShared import read_and_transform_json, setup_entry_components, unload_entry_components, BrematicProJsonDownloadView, BrematicProCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the BrematicPro component."""
    view = BrematicProJsonDownloadView()
    hass.http.register_view(view)
    #async_track_time_interval(hass, functools.partial(fetch_sensor_states, hass), timedelta(minutes=1))
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    if entry.entry_id not in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id] = {"coordinator": None, "entities": []}
        
    system_code = entry.data.get(CONF_SYSTEM_CODE, None)
    devices_filename = entry.data.get(CONF_CONFIG_FILE, 'BrematicPro.json')
    rooms_filename = entry.data.get(CONF_ROOMS_FILE, 'BrematicProRooms.json')
    gateways = entry.data.get(CONF_INTERNAL_GATEWAYS, [])

    success = await read_and_transform_json(hass, entry, devices_filename, rooms_filename, system_code)
    #_LOGGER.debug("async_setup_entry calls setup_entry_components")
    
    #Read Gateway sensors
    if not hass.data[DOMAIN][entry.entry_id]["coordinator"]:
        coordinator = BrematicProCoordinator(hass, entry)
        await coordinator.async_config_entry_first_refresh()
        if not coordinator.last_update_success:
            raise ConfigEntryNotReady
        hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    await setup_entry_components(hass, entry)#Setup components
    
    return True

async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update a given config entry."""
    #_LOGGER.debug("async_update_entry")
    devices_filename = entry.data.get(CONF_CONFIG_FILE, 'BrematicPro.json')
    rooms_filename = entry.data.get(CONF_ROOMS_FILE, 'BrematicProRooms.json')
    
    success = await read_and_transform_json(hass, entry, devices_filename, rooms_filename)

    if success:
        _LOGGER.info("Configuration successfully updated for BrematicPro.")
        return True
    else:
        _LOGGER.error("Failed to load or transform data for BrematicPro")
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    _LOGGER.info("Unloading BrematicPro entry.")
    return await unload_entry_components(hass, entry)