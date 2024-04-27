import json
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN, CONF_INTERNAL_JSON, CONF_SYSTEM_CODE

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

def read_and_transform_json(hass: HomeAssistant, entry, config_json, rooms_json, system_code = ''):
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
    if system_code == '':
        system_code = entry.data.get(CONF_SYSTEM_CODE, 'Invalid_Code')
    transformed_data = []
    for item in devices.values():
        device_name = item['name']
        room_name = 'Unknown'
        for room in rooms:
            if room in device_name:
                room_name = room
                device_name = device_name.replace(room, '').strip()
        freq = 868 if item['sys'] == 'B8' else 433 if item['sys'] == 'B4' else 0
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
    _LOGGER.debug(f"Generated JSON data: {json_data}")
    hass.config_entries.async_update_entry(entry, data={**entry.data, CONF_INTERNAL_JSON: json_data})
    return True

async def setup_entry_components(hass: HomeAssistant, entry):
    """Setup entry components for 'switch' and 'light'."""
    await hass.config_entries.async_forward_entry_setup(entry, 'switch')
    await hass.config_entries.async_forward_entry_setup(entry, 'light')

async def unload_entry_components(hass: HomeAssistant, entry):
    """Unload entry components for 'switch' and 'light'."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, 'switch') and \
                await hass.config_entries.async_forward_entry_unload(entry, 'light')
    return unload_ok

def send_command(self, url):
    """Send command to the Brematic device."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.status
    except requests.RequestException as error:
        _LOGGER.error("Error sending command to %s: %s", url, error)
        return 0

class BrematicProJsonDownloadView(HomeAssistantView):
    """View to download the CONF_INTERNAL_JSON data."""
    _LOGGER.warning(f"BrematicProJsonDownloadView called Start")
    url = "/api/brematicpro/download_json"
    name = "api:brematicpro:download_json"
    requires_auth = False

    async def get(self, request):
        """Return JSON data as file download."""
        hass = request.app['hass']

        # Access the user safely
        user = request.get('hass_user')
        if not user:
            _LOGGER.error("No user information found in request.")
            return web.Response(status=401, text="Unauthorized")

        # Check if the user is authenticated
        if not user.is_authenticated:
            _LOGGER.error("Access denied: unauthenticated access attempt.")
            return web.Response(status=401, text="Unauthorized")
        
        entry = next((e for e in hass.config_entries.async_entries(DOMAIN) if CONF_INTERNAL_JSON in e.data), None)
        if entry:
            json_data = entry.data[CONF_INTERNAL_JSON]
            _LOGGER.warning(f"BrematicProJsonDownloadView called Data")
            return web.Response(body=json_data, content_type='application/json', headers={
                'Content-Disposition': 'attachment; filename="BrematicProDevices.json"'
            })
        _LOGGER.warning(f"BrematicProJsonDownloadView called 404")
        return web.Response(body={}, content_type='application/json', headers={
            'Content-Disposition': 'attachment; filename="BrematicProDevices.json"'
        })
        #return web.Response(status=404, text="Configuration data not found.")
