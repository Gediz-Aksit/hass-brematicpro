import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.siren import SirenEntity, SirenEntityFeature
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .BrematicProShared import send_command, BrematicProEntityWithCommands

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up BrematicPro device from a config entry."""
    from .BrematicProShared import async_common_setup_entry
    
    return await async_common_setup_entry(hass, entry, async_add_entities, BrematicProSiren)

class BrematicProSiren(SirenEntity, BrematicProEntityWithCommands):
    """Representation of a BrematicPro Siren."""
    _type = 'siren'

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SirenEntityFeature.TURN_ON | SirenEntityFeature.TURN_OFF

    #@property
    #def icon(self):
    #    return "mdi:alarm-light"
