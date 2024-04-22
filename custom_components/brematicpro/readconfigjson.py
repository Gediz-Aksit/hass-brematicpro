import json
import logging
from homeassistant.helpers.json import save_json

_LOGGER = logging.getLogger(__name__)

def read_and_transform_json(hass, devices_filename, rooms_filename):
    devices_json_path = hass.config.path(devices_filename)
    rooms_json_path = hass.config.path(rooms_filename)
    try:
        with open(rooms_json_path, 'r') as file:
            rooms = json.load(file)
        with open(devices_json_path, 'r') as file:
            devices = json.load(file)
            transformed_data = []
            for item in devices.values():
                device_name = item['name']
                room_name = 'Unknown'
                for room in rooms:
                    if room in device_name:
                        room_name = room
                        device_name = device_name.replace(room, '').strip()
                freq = 868 if item['sys'] == 'B8' else 433 if item['sys'] == 'B4' else 0
                commands = {cmd: item['local'] + item['commands'][cmd]['url'] for cmd in item['commands']}
                transformed_data.append({
                    "uniqueid": item.get('address', 'NoID'),
                    "name": device_name,
                    "room": room_name,
                    "freq": freq,
                    "type": item['type'],
                    "commands": commands
                })
            return transformed_data
    except Exception as e:
        _LOGGER.error(f"Error processing JSON files: {str(e)}")
        return None

def save_data_to_file(hass, data, filename):
    """Save transformed data to a JSON file."""
    file_path = hass.config.path(filename)
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
        _LOGGER.info("Data successfully saved to %s", file_path)
    except Exception as e:
        _LOGGER.error("Failed to write data to file %s: %s", file_path, str(e))
