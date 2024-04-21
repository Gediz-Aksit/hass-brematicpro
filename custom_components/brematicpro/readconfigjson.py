import json
import logging
from homeassistant.core import HomeAssistant
from .const import CONF_CONFIG_JSON, DOMAIN

_LOGGER = logging.getLogger(__name__)

def read_and_transform_json(hass: HomeAssistant, entry):
    """Read and transform the JSON configuration file."""
    path = hass.config.path(entry.data[CONF_CONFIG_JSON])

    try:
        with open(path, 'r') as file:
            data = json.load(file)
            transformed_data = []

            for item in data.values():
                freq = 0  # Default frequency
                if item['sys'] == 'B8':
                    freq = 868
                elif item['sys'] == 'B4':
                    freq = 433

                commands = {cmd: item['local'] + item['commands'][cmd]['url']
                            for cmd in item['commands']}

                transformed_data.append({
                    "uniqueid": item['address'],
                    "name": item['name'],
                    "freq": freq,
                    "type": item['type'],
                    "commands": commands
                })

            return transformed_data

    except FileNotFoundError:
        _LOGGER.error("File not found: %s", path)
    except json.JSONDecodeError:
        _LOGGER.error("Error decoding JSON from file: %s", path)
    except Exception as e:
        _LOGGER.error("An error occurred: %s", e)
    return None

def save_data_to_file(hass: HomeAssistant, data, filename):
    """Save transformed data to a JSON file within Home Assistant's configuration directory."""
    path = hass.config.path(filename)  # Ensures file is saved in the config directory

    try:
        with open(path, 'w') as file:
            json.dump(data, file, indent=2)
        _LOGGER.info("Data successfully saved to %s", path)
    except Exception as e:
        _LOGGER.error("Failed to write data to file %s: %s", path, e)