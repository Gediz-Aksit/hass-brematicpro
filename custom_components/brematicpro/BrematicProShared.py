import requests
import json
import logging
import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta

from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_INTERNAL_CONFIG_JSON, CONF_INTERNAL_GATEWAYS, CONF_INTERNAL_SENSOR_JSON

_LOGGER = logging.getLogger(__name__)

class BrematicProCoordinator(DataUpdateCoordinator):
    """Class to manage fetching BrematicPro data."""

    def __init__(self, hass, system_code, gateways):
        """Initialize."""
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
        #if not self.gateways:
        #    raise UpdateFailed("No gateway IPs are configured")
        data = {}
        if self.gateways:
            async with aiohttp.ClientSession() as session:
                for domain_or_ip in self.gateways:
                    url = f"{domain_or_ip}/cmd?XC_FNC=getStates&at={self.system_code}"
                    _LOGGER.debug(f"URL {url}")
                    try:
                        async with session.get(url) as response:
                            _LOGGER.debug(f"Received response from {domain_or_ip} with HTTP status: {response.status}")
                            if response.status == 200:
                                response_text = await response.text()
                                data[domain_or_ip] = json.loads(await response.text())
                                _LOGGER.debug('_async_update_data ' + json.dumps(data, indent=2))#Posting statuses
                                _LOGGER.debug(f"Data for {domain_or_ip}: {data[domain_or_ip]}")
                            else:
                                raise UpdateFailed(f"Failed to fetch data from {domain_or_ip}: HTTP {response.status}")
                    except aiohttp.ClientError as e:
                        raise UpdateFailed(f"Error contacting {domain_or_ip}: {str(e)}")
        return data

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
    #_LOGGER.debug(f"Generated JSON data: {json_data}")
    #hass.config_entries.async_update_entry(entry, data={CONF_INTERNAL_CONFIG_JSON: json.dumps(transformed_data)})
    hass.config_entries.async_update_entry(entry, data={**entry.data, CONF_INTERNAL_CONFIG_JSON: json_data, CONF_INTERNAL_GATEWAYS: list(gateways)})
    #hass.config_entries.async_update_entry(entry, data={CONF_INTERNAL_CONFIG_JSON: json_data, CONF_INTERNAL_GATEWAYS: list(gateways)})
    return True

async def async_common_setup_entry(hass, entry, async_add_entities, device_types, entity_class):
    """Common setup for BrematicPro devices."""
    json_data = entry.data.get(CONF_INTERNAL_CONFIG_JSON, {})
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    _LOGGER.debug("async_common_setup_entry")
    if json_data:
        devices = json.loads(json_data)
        entities = []
        _LOGGER.debug("async_common_setup_entry A")
        #existing_entities = {entity.unique_id: entity for entity in hass.data.get(DOMAIN, {}).get(entry.entry_id, [])}
        for device in devices:
            device_type = device.get('type', None)
            _LOGGER.debug("async_common_setup_entry B")
            if device['type'] in device_types:
                _LOGGER.debug("async_common_setup_entry C")
                unique_id = device['uniqueid']
                existing_entity = next((e for e in hass.data[DOMAIN][entry.entry_id]["entities"] if e.unique_id == unique_id), None)
                #area_id = find_area_id(hass, device.get('room'))
                
                if existing_entity:
                    existing_entity.update_device(device)
                else:
                    entity = entity_class(device, hass)
                    entities.append(entity)                
                #existing_entities.async_update_entity(entity_id, new_area_id=area_id)
                #existing_entities.async_update_entity(entity_id, new_area_id=area_id)
        async_add_entities(entities, True)
        _LOGGER.debug("async_common_setup_entry End")
        #if DOMAIN not in hass.data:
        #    hass.data[DOMAIN] = {}
        #if entry.entry_id not in hass.data[DOMAIN]:
        #    hass.data[DOMAIN][entry.entry_id] = {}
        #hass.data[DOMAIN][entry.entry_id]["entities"] = entities
        return True
    return False

async def setup_entry_components(hass: HomeAssistant, entry):
    """Setup entry components for BrematicPro devices."""
	from .switch import BrematicProSwitch, BrematicProMeteredSwitch, BrematicProLight
	from .sensor import BrematicProDoor, BrematicProWindow
	
    await async_common_setup_entry(hass, entry, 'switch', BrematicProSwitch)
    await async_common_setup_entry(hass, entry, 'smartswitch', BrematicProMeteredSwitch)
    await async_common_setup_entry(hass, entry, 'light', BrematicProLight)
    await async_common_setup_entry(hass, entry, 'door', BrematicProDoor)
    await async_common_setup_entry(hass, entry, 'window', BrematicProWindow)

async def unload_entry_components(hass: HomeAssistant, entry):
    """Unload entry components for BrematicPro devices."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, 'switch') and \
                await hass.config_entries.async_forward_entry_unload(entry, 'smartswitch') and \
                await hass.config_entries.async_forward_entry_unload(entry, 'light') and \
                await hass.config_entries.async_forward_entry_unload(entry, 'door') and \
                await hass.config_entries.async_forward_entry_unload(entry, 'window')
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
