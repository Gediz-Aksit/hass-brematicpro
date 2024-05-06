import requests
import json
import logging
import aiohttp
from itertools import product
from enum import Enum
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_INTERNAL_CONFIG_JSON, CONF_INTERNAL_GATEWAYS, CONF_INTERNAL_SENSOR_JSON

_LOGGER = logging.getLogger(__name__)

class BrematicProCoordinator(DataUpdateCoordinator):
    """Class to manage fetching BrematicPro data."""

    def __init__(self, hass, entry, system_code, gateways):
        """Initialize."""
        self.entry = entry
        self.system_code = system_code
        self.gateways = gateways
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name="BrematicPro",
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        _LOGGER.debug("Fetch data from API.")
        if self.gateways:
            async with aiohttp.ClientSession() as session:
                BrematicPro_entities = self.hass.data[DOMAIN][self.entry.entry_id].get("entities", [])
                for domain_or_ip in self.gateways:
                    url = f"{domain_or_ip}/cmd?XC_FNC=getStates&at={self.system_code}"
                    _LOGGER.debug(f"URL {url}")
                    try:
                        async with session.get(url) as response:
                            _LOGGER.debug(f"Received response from {domain_or_ip} with HTTP status: {response.status}")
                            if response.status == 200:
                                response_text = await response.text()
                                device_states = json.loads(response_text).get('XC_SUC', [])
                                relevant_entities = list(filter(lambda ent: ent.frequency == 868, BrematicPro_entities))# Filter entities to include only those with a frequency of 868
                                matching_pairs = list(filter(lambda pair: pair[0].unique_id == pair[1]['adr'], product(relevant_entities, device_states)))# Find the entities that matches the 'adr' key
                                [entity.update_state(device_state) for entity, device_state in matching_pairs if entity.unique_id == device_state['adr']]# Update the status of matching entities
                                key_values_str = ', '.join(map(lambda pair: ', '.join(pair[1].keys()), matching_pairs))
                                _LOGGER.debug(f"Keys from matching device states: {key_values_str}")
                                _LOGGER.debug('_async_update_data ' + json.dumps(json.loads(response_text), indent=2))#Posting statuses
                            else:
                                raise UpdateFailed(f"Failed to fetch data from {domain_or_ip}: HTTP {response.status}")
                    except aiohttp.ClientError as e:
                        raise UpdateFailed(f"Error contacting {domain_or_ip}: {str(e)}")

class BatteryState(Enum):
    GOOD = 'good'
    LOW = 'low'
    UNKNOWN = 'unknown'
    WIRED = 'wired'

class BrematicProDevice(Entity):
    """Representation of a BrematicPro device."""
    _type = 'unknown_device'

    def __init__(self, device, hass):
        """Initialize the device."""
        self._unique_id = device['uniqueid']
        self._name = device['name']
        self._frequency =  device.get('freq', None)
        self._suggested_area = device.get('room', None)
        self._is_on = False
        self._session = async_get_clientsession(hass)
        self._battery_state = BatteryState.UNKNOWN

    @property
    def unique_id(self):
        """Return the unique ID of the device."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def device_type(self):
        """Return the device type."""
        return self._type

    @property
    def frequency(self):
        """Return the device frequency."""
        return self._frequency

    @property
    def battery_state(self):
        """Return the battery state of the device."""
        return self._battery_state.value
        
    def update_state(self, device_state):
        """Updates device state if applicable."""
        _LOGGER.warning('Unhandled BrematicProDevice got the update ' + json.dumps(device_state, indent=2))#Posting update

async def async_common_setup_entry(hass, entry, async_add_entities, entity_class):
    """Common setup for BrematicPro devices."""
    json_data = entry.data.get(CONF_INTERNAL_CONFIG_JSON, {})
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    if json_data:
        devices = json.loads(json_data)
        entities = []
        _LOGGER.debug(f"async_common_setup_entry for {entity_class._type}")
        for device in devices:
            if device.get('type', 'Invalid') == entity_class._type:
                unique_id = device['uniqueid']
                existing_entity = next((e for e in hass.data[DOMAIN][entry.entry_id]["entities"] if e.unique_id == unique_id), None)
                #area_id = find_area_id(hass, device.get('room'))
                if existing_entity:
                    existing_entity.update_device(device)
                else:
                    entity = entity_class(device, hass)
                    entities.append(entity)
        async_add_entities(entities, True)
        if "entities" not in hass.data[DOMAIN][entry.entry_id]:
            hass.data[DOMAIN][entry.entry_id]["entities"] = []
        hass.data[DOMAIN][entry.entry_id]["entities"].extend(entities)
        return True
    return False

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
    _LOGGER.debug("read_and_transform_json")
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
        system_code = entry.data.get(CONF_SYSTEM_CODE, "")
    transformed_data = []
    gateways = set()  # Using a set to prevent duplicates
    for item in devices.values():
        device_name = item.get('name','')
        item_type = item.get('type', None)
        room_name = 'Unknown'
        for room in rooms:
            if room in device_name:
                room_name = room
                device_name = device_name.replace(room, '').strip()
        item_sys = item.get('sys')
        freq = 868 if item_sys == 'B8' else 433 if item_sys == 'B4' else 0
        item_local = item.get('local', '')
        item_commands = item.get('commands', [])
        if item_local:
            gateways.add(item_local)
        commands = {cmd: f"{item_local}{item_commands[cmd]['url']}&at={system_code}" for cmd in item_commands}

        transformed_data.append({
            "uniqueid": item.get('address', 'NoID'),
            "name": device_name,
            "room": room_name,
            "freq": freq,
            "type": item_type,
            "commands": commands
        })
    json_data = json.dumps(transformed_data)
    hass.config_entries.async_update_entry(entry, data={**entry.data, CONF_INTERNAL_CONFIG_JSON: json_data, CONF_INTERNAL_GATEWAYS: list(gateways)})
    return True

async def setup_entry_components(hass: HomeAssistant, entry):
    """Setup entry components for BrematicPro devices."""
    await hass.config_entries.async_forward_entry_setup(entry, 'switch')
    await hass.config_entries.async_forward_entry_setup(entry, 'light')
    await hass.config_entries.async_forward_entry_setup(entry, 'sensor')

async def unload_entry_components(hass: HomeAssistant, entry):
    """Unload entry components for BrematicPro devices."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, 'switch') and \
                await hass.config_entries.async_forward_entry_unload(entry, 'light') and \
                await hass.config_entries.async_forward_entry_unload(entry, 'sensor')
    return unload_ok

async def send_command(url):
    """Send command to the Brematic device."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as response:
                response.raise_for_status()  # This will raise an error for bad HTTP status
                return response.status
        except aiohttp.ClientError as error:
            _LOGGER.error("Error sending command to %s: %s", url, error)
            return 0

class BrematicProJsonDownloadView(HomeAssistantView):
    """View to download the CONF_INTERNAL_CONFIG_JSON data."""
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
        
        entry = next((e for e in hass.config_entries.async_entries(DOMAIN) if CONF_INTERNAL_CONFIG_JSON in e.data), None)
        if entry:
            json_data = entry.data[CONF_INTERNAL_CONFIG_JSON]
            _LOGGER.warning(f"BrematicProJsonDownloadView called Data")
            return web.Response(body=json_data, content_type='application/json', headers={
                'Content-Disposition': 'attachment; filename="BrematicProDevices.json"'
            })
        _LOGGER.warning(f"BrematicProJsonDownloadView called 404")
        return web.Response(body={}, content_type='application/json', headers={
            'Content-Disposition': 'attachment; filename="BrematicProDevices.json"'
        })
        #return web.Response(status=404, text="Configuration data not found.")