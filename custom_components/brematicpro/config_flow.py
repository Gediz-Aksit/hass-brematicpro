from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_CONFIG_JSON, CONF_ROOMS_JSON
from .readconfigjson import read_and_transform_json, setup_entry_components

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
        errors = {}

        if user_input is not None:
		
            entry = self.hass.config_entries.async_get_entry(self.context.get("entry_id"))
            if entry:
                self.hass.config_entries.async_update_entry(entry, data=user_input)
            else:
                return self.async_create_entry(title="BrematicPro", data=user_input)
		
            if user_input.get('read_json'):
                success = await self.hass.async_add_executor_job(
                    read_and_transform_json,
                    self.hass,
                    entry,
                    user_input[CONF_CONFIG_JSON],
                    user_input[CONF_ROOMS_JSON],
					user_input[CONF_SYSTEM_CODE]
                )
                if not success:
                    errors['read_json'] = "Failed to read or transform JSON"

            if user_input.get('process_data'):
                await setup_entry_components(self.hass, entry)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SYSTEM_CODE, default=''): str,
                vol.Required(CONF_CONFIG_JSON, default='BrematicPro.json'): str,
                vol.Optional(CONF_ROOMS_JSON, default='BrematicProRooms.json'): str,
                vol.Optional('read_json', default=False): bool,
                vol.Optional('process_data', default=False): bool
            }),
            errors=errors,
            description_placeholders={
                "download_url": "/api/brematicpro/download_json"
            }
        )
