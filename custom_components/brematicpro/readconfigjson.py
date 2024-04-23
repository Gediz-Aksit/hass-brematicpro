import json
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from .const import CONF_INTERNAL_JSON

_LOGGER = logging.getLogger(__name__)

def find_area_id(hass, room_name):
    """Find area ID by matching room name with area names."""
    if room_name:
        room_name = room_name.lower().strip()
        area_registry = ar.async_get(hass)
        for area in area_registry.areas.values():
            if area.name.lower().strip() == room_name:
                _LOGGER.debug(f"Match found: {area.name}")
                return area.id
        _LOGGER.debug("No match found")
    return None

def read_and_transform_json(hass: HomeAssistant, entry, config_json, rooms_json):
    """Reads and transforms JSON data from specified files and updates entry data."""
    config_json_path = hass.config.path(config_json)
    rooms_json_path = hass.config.path(rooms_json)

    try:
        with open(rooms_json_path, 'r') as file:
            rooms = json.load(file)
        with open(config_json_path, 'r') as file:
            devices = json.load(file)
    except FileNotFoundError as e:
        _LOGGER.error(f"File not found: {e.filename}")
        return False
    except json.JSONDecodeError as e:
        _LOGGER.error("Error decoding JSON: %s", e)
        return False
    except Exception as e:
        _LOGGER.error(f"An unexpected error occurred: {e}")
        return False

    transformed_data = []
    for item in devices.values():
        device_name = item['name']
        room_name = 'Unknown'
        for room in rooms:
            if room in device_name:
                room_name = room
                device_name = device_name.replace(room, '').strip()
        freq = 868 if item['sys'] == 'B8' else 433 if item['sys'] == 'B4' else 0
        system_code = item.get('system_code', 'default_code')
        commands = {cmd: f"{item['local']}{item['commands'][cmd]['url']}&at={system_code}" for cmd in item['commands']}

        transformed_data.append({
            "uniqueid": item.get('address', 'NoID'),
            "name": device_name,
            "room": room_name,
            "freq": freq,
            "type": item['type'],
            "commands": commands
        })

    json_data = json.dumps(transformed_data)
    hass.config_entries.async_update_entry(entry, data={**entry.data, CONF_INTERNAL_JSON: json_data})
    _LOGGER.info("Configuration data updated successfully.")
    return True

async def setup_entry_components(hass: HomeAssistant, entry):
    """Setup entry components for 'switch' and 'light'."""
    await hass.config_entries.async_forward_entry_setup(entry, 'switch')
    await hass.config_entries.async_forward_entry_setup(entry, 'light')
    _LOGGER.info("Entry components 'switch' and 'light' set up successfully.")

async def unload_entry_components(hass: HomeAssistant, entry):
    """Unload entry components for 'switch' and 'light'."""
    unload_ok = all([
        await hass.config_entries.async_forward_entry_unload(entry, 'switch'),
        await hass.config_entries.async_forward_entry_unload(entry, 'light')
    ])
    if unload_ok:
        _LOGGER.info("Entry components 'switch' and 'light' unloaded successfully.")
    return unload_ok
