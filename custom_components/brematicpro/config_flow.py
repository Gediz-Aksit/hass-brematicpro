import logging
from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_CONFIG_FILE, CONF_ROOMS_FILE
from .BrematicProShared import read_and_transform_json, setup_entry_components

_LOGGER = logging.getLogger(__name__)

class BrematicProConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for BrematicPro."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        return await self.common_flow_handler(user_input)

    async def async_step_init(self, user_input=None):
        """Handle the initial step."""
        return await self.common_flow_handler(user_input)

    async def common_flow_handler(self, user_input):
        """Handle common logic for user and options flows."""
        #_LOGGER.debug("common_flow_handler")
        errors = {}
        _LOGGER.debug(f"Entry updated with user input: {user_input}")

        if user_input is not None:
            #_LOGGER.debug("common_flow_handler A")
            entry = self.hass.config_entries.async_get_entry(self.context.get("entry_id"))
            _LOGGER.debug(f"Entry retrieved: {entry}")
            if entry:
                self.hass.config_entries.async_update_entry(entry, data=user_input)
            else:
                return self.async_create_entry(title="BrematicPro", data=user_input)
        
            if user_input.get('read_json'):
                #_LOGGER.debug("common_flow_handler B")
                success = await read_and_transform_json(self.hass, entry, user_input[CONF_CONFIG_FILE], user_input[CONF_ROOMS_FILE], user_input[CONF_SYSTEM_CODE])
                if not success:
                    errors['read_json'] = "Failed to read or transform JSON"

            if user_input.get('process_data'):
                #_LOGGER.debug("Configuration. common_flow_handler calls setup_entry_components")
                await setup_entry_components(self.hass, entry)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SYSTEM_CODE, default=''): str,
                vol.Required(CONF_CONFIG_FILE, default='BrematicPro.json'): str,
                vol.Optional(CONF_ROOMS_FILE, default='BrematicProRooms.json'): str,
                vol.Optional('read_json', default=True): bool,
                vol.Optional('process_data', default=True): bool
            }),
            errors=errors,
            description_placeholders={
                "download_url": "/api/brematicpro/download_json"
            }
        )
