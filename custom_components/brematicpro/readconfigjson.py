import json
import os
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
                freq = 868 if item['sys'] == 'B8' else 433 if item['sys'] == 'B4' else 0
                commands = {cmd: item['local'] + item['commands'][cmd]['url'] for cmd in item['commands']}
                transformed_data.append({
                    "uniqueid": item['address'],
                    "name": item['name'],
                    "freq": freq,
                    "type": item['type'],
                    "commands": commands
                })

            # Save the transformed data to BrematicProDevices.json
            output_path = hass.config.path('BrematicProDevices.json')
            with open(output_path, 'w') as outfile:
                json.dump(transformed_data, outfile, indent=4)
            _LOGGER.info("Transformed data saved to %s", output_path)

    except FileNotFoundError:
        _LOGGER.error("File not found: %s", path)
    except json.JSONDecodeError:
        _LOGGER.error("Error decoding JSON from file: %s", path)
    except Exception as e:
        _LOGGER.error("An error occurred: %s", e)

