import json
import logging
from homeassistant.helpers.json import save_json

_LOGGER = logging.getLogger(__name__)
DOMAIN = "brematicpro"  # Ensure this constant is correctly defined here or imported if defined elsewhere.

def read_and_transform_json(hass, devices_filename='BrematicPro.json', rooms_filename='BrematicProRooms.json'):
    devices_json_path = hass.config.path(devices_filename)
    rooms_json_path = hass.config.path(rooms_filename)

    try:
        with open(rooms_json_path, 'r') as file:
            rooms = json.load(file)
        with open(devices_json_path, 'r') as file:
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

        # Augment commands with the local URL
        commands = {cmd: item['local'] + item['commands'][cmd]['url'] for cmd in item['commands']}

        transformed_data.append({
            "uniqueid": item.get('address', 'NoID'),  # Default 'NoID' if no address is provided
            "name": device_name,
            "room": room_name,
            "freq": freq,
            "type": item['type'],
            "commands": commands
        })

    # Store the data in Home Assistant's internal storage
    hass.data[DOMAIN] = transformed_data
    return transformed_data
