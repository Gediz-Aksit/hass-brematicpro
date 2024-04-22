import json
import logging
from homeassistant.helpers import area_registry as ar

_LOGGER = logging.getLogger(__name__)

def find_area_id(hass, room_name):
    """Find area ID by matching room name with area names."""
    if room_name:
        room_name = room_name.lower().strip()  # Normalize the room name
        area_registry = ar.async_get(hass)
        for area in area_registry.areas.values():
            if area.name.lower().strip() == room_name:
                _LOGGER.debug(f"Match found: {area.name}")
                return area.id
        _LOGGER.debug("No match found")
    return None

def read_and_transform_json(hass, config_json='BrematicProConfig.json', rooms_json='BrematicProRooms.json'):
    config_json_path = hass.config.path(config_json)
    rooms_json_path = hass.config.path(rooms_json)

    try:
        with open(rooms_json_path, 'r') as file:
            rooms = json.load(file)
        with open(config_json_path, 'r') as file:
            devices = json.load(file)

    except FileNotFoundError as e:
        _LOGGER.error(f"File not found: {e.filename}")
        return None
    except json.JSONDecodeError as e:
        _LOGGER.error("Error decoding JSON: %s", e)
        return None
    except Exception as e:
        _LOGGER.error(f"An unexpected error occurred: {e}")
        return None

    transformed_data = []
    for item in devices.values():
        device_name = item['name']
        room_name = 'Unknown'  # Default if no room is found

        # Extract the room from the device name
        for room in rooms:
            if room in device_name:
                room_name = room
                device_name = device_name.replace(room, '').strip()

        # Assuming 'sys' field maps directly to frequency
        freq = 868 if item['sys'] == 'B8' else 433 if item['sys'] == 'B4' else 0

        # Retrieve system_code from config and integrate it into command URLs
        system_code = item.get('system_code', 'default_code')

        # Augment commands with the local URL and system_code with correct parameter name
        commands = {cmd: f"{item['local']}{item['commands'][cmd]['url']}&at={system_code}" for cmd in item['commands']}

        transformed_data.append({
            "uniqueid": item.get('address', 'NoID'),  # Default 'NoID' if no address is provided
            "name": device_name,
            "room": room_name,
            "freq": freq,
            "type": item['type'],
            "commands": commands
        })

    return transformed_data
