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
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity, UpdateFailed
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_INTERNAL_CONFIG_JSON, CONF_INTERNAL_GATEWAYS, CONF_INTERNAL_SENSOR_JSON

_LOGGER = logging.getLogger(__name__)

class BrematicProCoordinator(DataUpdateCoordinator):
    """Class to manage fetching BrematicPro data."""

    def __init__(self, hass, entry):
        """Initialize."""
        self.entry = entry
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        _LOGGER.debug("Fetch data from API.")
        self.entry.data.get(CONF_SYSTEM_CODE, "")
        system_code = self.entry.data.get(CONF_SYSTEM_CODE, "")
        gateways = self.entry.data.get(CONF_INTERNAL_GATEWAYS, [])
        _LOGGER.debug(f"_async_update_data DOMAIN {DOMAIN}")
        _LOGGER.debug(f"_async_update_data entity id {self.entry.entry_id}")
        if gateways:
            async with aiohttp.ClientSession() as session:
                BrematicPro_entities = self.hass.data[DOMAIN][self.entry.entry_id].get("entities", [])
                if BrematicPro_entities:
                    _LOGGER.debug(f"Entity UID count {len(BrematicPro_entities)}")
                    _LOGGER.debug(f"Entity 1 UID {BrematicPro_entities[0].unique_id}")
                else:
                    _LOGGER.debug("BrematicPro_entities list is empty")
                if BrematicPro_entities:
                    for domain_or_ip in gateways:
                        url = f"{domain_or_ip}/cmd?XC_FNC=getStates&at={system_code}"
                        _LOGGER.debug(f"URL {url}")
                        try:
                            async with session.get(url) as response:
                                _LOGGER.debug(f"Received response from {domain_or_ip} with HTTP status: {response.status}")
                                if response.status == 200:
                                    response_text = await response.text()
                                    device_states = json.loads(response_text).get('XC_SUC', [])
                                    relevant_entities = list(filter(lambda ent: ent.frequency == 868, BrematicPro_entities))# Filter entities to include only those with a frequency of 868
                                    if relevant_entities:
                                        _LOGGER.debug(f"R Entity UID count {len(relevant_entities)}")
                                        _LOGGER.debug(f"R Entity 1 UID {relevant_entities[0].unique_id}")
                                    else:
                                        _LOGGER.debug("relevant_entities list is empty")
                                    if device_states:
                                        _LOGGER.debug(f"State UID count {len(device_states)}")
                                        _LOGGER.debug(f"State 1 UID {device_states[0]['adr']}")
                                    else:
                                        _LOGGER.debug("device_states list is empty")
                                    matching_device_states = [device_state for entity, device_state in product(relevant_entities, device_states) if entity.unique_id == device_state['adr']]
                                    for temp_device_state in matching_device_states:
                                        if len(temp_device_state['adr']) > 6:#Unique ID needs to be longer than 6 characters. Just an assuption.
                                            lEntity = list(filter(lambda entity: temp_device_state['adr'] in entity.unique_id, relevant_entities))
                                            for entity in lEntity:
                                                if entity.device_name == 'temperature' or entity.device_name == 'water' or entity.device_name == 'motion':
                                                    _LOGGER.debug(f'entity {entity.device_name} {entity.unique_id} {temp_device_state}')
                                                if entity.unique_id == '74230189116E':
                                                    _LOGGER.debug(f'battery entity {entity.device_name} {entity.unique_id} {temp_device_state}')
                                                entity.update_state(temp_device_state)
                                else:
                                    _LOGGER.warning(f"Failed to fetch data from {domain_or_ip}: HTTP {response.status}")
                        except aiohttp.ClientError as e:
                            _LOGGER.warning(f"Error contacting {domain_or_ip}: {str(e)}")

class BrematicProEntity(CoordinatorEntity):
    """Representation of a BrematicPro entity."""
    _type = 'unknown_entity'
    _has_battery = False

    def __init__(self, hass, coordinator, device, device_entry):
        """Initialize the device."""
        super().__init__(coordinator)
        self.hass = hass
        self.device = device
        self._device_id = device_entry.id
        self._attr_unique_id = f"{device['unique_id']}_{self._type}"
        self._attr_device_info = {
            'identifiers': {(DOMAIN, device_entry.id)},
            'name': device_entry.name,
            'manufacturer': device_entry.manufacturer,
            #'model': device_entry.model,
            'via_device': (DOMAIN, device_entry.via_device_id) if device_entry.via_device else None
        }
        self._frequency =  device.get('frequency', None)        

    async def async_added_to_hass(self):
        """Register as a listener when added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    @property
    def unique_id(self):
        """Return the unique ID of the device."""
        return self._unique_id

    @property
    def frequency(self):
        """Return the device frequency."""
        return self._frequency

    @property
    def has_battery(self):
        """Return the device frequency."""
        return self._has_battery
        
    def update_device(self, device, device_id):
        self.device_info = device_info
        self._device_id = device_id
        self._attr_unique_id = f"{device_info['unique_id']}_{self.entity_name()}"
        self._attr_device_info = self.get_device_info()
        self._frequency =  device.get('frequency', None)

    def update_state(self, device_state):
        """Updates device state if applicable."""
        #_LOGGER.warning('Unhandled BrematicProEntity got the update ' + json.dumps(device_state, indent=2))#Posting update

async def async_common_setup_entry(hass, entry, async_add_entities, entity_class):
    from.sensor import BrematicProHumidity
    from.binary_sensor import BrematicProBattery
    
    """Common setup for BrematicPro devices."""
    json_data = entry.data.get(CONF_INTERNAL_CONFIG_JSON, {})
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    if json_data:
        devices = json.loads(json_data)
        entities = []
        device_registry = hass.helpers.device_registry.async_get(hass)#await hass.helpers.device_registry.async_get_registry()
        entity_registry = hass.helpers.entity_registry.async_get(hass)#await hass.helpers.entity_registry.async_get_registry()
        _LOGGER.debug(f"async_common_setup_entry for {entity_class._type}. Device zero {devices[0]}")
        for device in devices:
            if device.get('type', 'Invalid') == entity_class._type:
                device_id = (DOMAIN, device['unique_id'])
                device_entry = device_registry.async_get_device({device_id}, [])
                if not device_entry:
                    # Device not found, create a new one
                    device_entry = device_registry.async_get_or_create(
                        config_entry_id=entry.entry_id,
                        identifiers={device_id},
                        manufacturer='Brennenstuhl',
                        model='BrematicPRO',
                        name=device['name'],
                        suggested_area=device.get('room', None)#,
                        #sw_version="Software Version"
                    )
                unique_entity_id = f"{DOMAIN}_{device['unique_id']}_{entity_class._type}"
                if not entity_registry.async_get(unique_entity_id):
                    entity = entity_class(hass, coordinator, device, device_entry)
                    entities.append(entity)
                if device.get('frequency', 0) == 868:
                    if device.get('device_name', '') == 'temperature':
                        if not entity_registry.async_get(f"{DOMAIN}_{device['unique_id']}_humidity"):
                            entities.append(BrematicProHumidity(hass, coordinator, device, device_entry))
                    if device.get('has_battery', False):
                        if not entity_registry.async_get(f"{DOMAIN}_{device['unique_id']}_battery"):
                            entities.append(BrematicProBattery(hass, coordinator, device, device_entry))
        async_add_entities(entities, True)
        if "entities" not in hass.data[DOMAIN][entry.entry_id]:
            hass.data[DOMAIN][entry.entry_id]["entities"] = []
        hass.data[DOMAIN][entry.entry_id]["entities"].extend(entities)
        _LOGGER.debug(f"async_common_setup_entry DOMAIN {DOMAIN}")
        _LOGGER.debug(f"async_common_setup_entry entity ID {entry.entry_id}")
        if len(entities) > 0:
            _LOGGER.debug(f"Adding {len(entities)} new entities (first): {entities[0]}")
            _LOGGER.debug(f"Final entities list (first with unique id): {hass.data[DOMAIN][entry.entry_id]['entities'][0].unique_id} {hass.data[DOMAIN][entry.entry_id]['entities'][0]}")
        else:
            _LOGGER.debug("Empty entities")
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
        item_name = item.get('type', None)
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
            "unique_id": item.get('address', 'NoID'),
            "name": device_name,
            "room": room_name,
            "frequency": freq,
            "type": item_name,
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
    await hass.config_entries.async_forward_entry_setup(entry, 'binary_sensor')

async def unload_entry_components(hass: HomeAssistant, entry):
    """Unload entry components for BrematicPro devices."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, 'switch') and \
                await hass.config_entries.async_forward_entry_unload(entry, 'light') and \
                await hass.config_entries.async_forward_entry_unload(entry, 'sensor') and \
                await hass.config_entries.async_forward_entry_unload(entry, 'binary_sensor')
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
            return web.Response(body=json_data, content_name='application/json', headers={
                'Content-Disposition': 'attachment; filename="BrematicProEntitys.json"'
            })
        _LOGGER.warning(f"BrematicProJsonDownloadView called 404")
        return web.Response(body={}, content_name='application/json', headers={
            'Content-Disposition': 'attachment; filename="BrematicProEntitys.json"'
        })
        #return web.Response(status=404, text="Configuration data not found.")