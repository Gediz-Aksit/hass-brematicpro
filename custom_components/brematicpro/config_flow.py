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

    async def common_flow_handler(self, user_input):
        """Handle common logic for user and options flows."""
        errors = {}

        if user_input is not None:
            if 'read_json' in user_input and user_input['read_json']:
                success = await self.hass.async_add_executor_job(
                    read_and_transform_json,
                    self.hass,
                    user_input[CONF_CONFIG_JSON],
                    user_input[CONF_ROOMS_JSON]
                )
                if not success:
                    errors['read_json'] = "Failed to read or transform JSON"

            if 'process_data' in user_input and user_input['process_data']:
                await setup_entry_components(self.hass)

            if not errors:
                return self.async_create_entry(title="BrematicPro", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SYSTEM_CODE, default='Enter your system code here'): str,
                vol.Required(CONF_CONFIG_JSON, default='BrematicPro.json'): str,
                vol.Required(CONF_ROOMS_JSON, default='BrematicProRooms.json'): str,
                vol.Optional('read_json', default=False): bool,
                vol.Optional('process_data', default=False): bool,
            }),
            errors=errors
        )

class BrematicProOptionsFlow(config_entries.OptionsFlow):
    """Options flow for BrematicPro."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data=user_input
        )
