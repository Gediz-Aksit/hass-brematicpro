import json
import logging
import requests
from homeassistant.components.light import LightEntity
from .const import DOMAIN, CONF_INTERNAL_JSON

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up BrematicPro lights from a config entry."""
    json_data = entry.data.get(CONF_INTERNAL_JSON)
    if json_data:
        devices = json.loads(json_data)
        area_registry = ar.async_get(hass)
        # Fetch existing entities or initialize an empty list
        existing_entities = {entity.unique_id: entity for entity in hass.data.get(DOMAIN, {}).get(entry.entry_id, [])}
        new_entities = []

        for device in devices:
            if device['type'] == 'light':
                unique_id = device['uniqueid']
                if unique_id in existing_entities:
                    # Update existing entity if necessary
                    entity = existing_entities[unique_id]
                    entity.update_device(device)
                else:
                    # Create a new entity if it doesn't exist
                    entity = BrematicLight(device, area_registry)
                    new_entities.append(entity)

        async_add_entities(new_entities, True)  # True to update state upon addition
        # Update the global data store for this entry
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = list(existing_entities.values()) + new_entities

class BrematicProLight(LightEntity):
    """Representation of a Brematic Light."""

    def __init__(self, device):
        """Initialize the light."""
        self._device = device
        self._is_on = False
        self._name = device["name"]
        self._on_command = device["commands"]["on"]
        self._off_command = device["commands"]["off"]

    @property
    def name(self):
        """Return the name of the light."""
        return self._name

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._is_on

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        self._send_command(self._on_command)
        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._send_command(self._off_command)
        self._is_on = False
        self.schedule_update_ha_state()

    def update(self):
        """Fetch new state data for this light."""
        # Here be logic to check the current state of the light if possible
        pass

    def _send_command(self, url):
        """Send command to the Brematic device."""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as error:
            _LOGGER.error("Error sending command to %s: %s", url, error)

    async def async_update(self):
        """Fetch new state data for this light."""
        self._available = True
