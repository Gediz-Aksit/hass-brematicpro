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
        return await self._common_flow_handler(self.hass, user_input)

    @staticmethod
    async def _common_flow_handler(hass, context, user_input):
        """Handle common logic for user and options flows."""
        errors = {}

        if user_input is not None:
            entry_id = context.get("entry_id")
            entry = hass.config_entries.async_get_entry(entry_id) if entry_id else None
            if 'read_json' in user_input and user_input['read_json']:
                success = await hass.async_add_executor_job(
                    read_and_transform_json,
                    hass,
                    entry,
                    user_input[CONF_CONFIG_JSON],
                    user_input[CONF_ROOMS_JSON]
                )
                if not success:
                    errors['read_json'] = "Failed to read or transform JSON"

            if 'process_data' in user_input and user_input['process_data']:
                await setup_entry_components(hass, entry)

            if not errors:
                return hass.config_entries.async_create_entry(title="BrematicPro", data=user_input)

        return hass.async_show_form(
            step_id="user" if "entry_id" in context else "init",
            data_schema=vol.Schema({
                vol.Required(CONF_SYSTEM_CODE, default='Enter your system code here'): str,
                vol.Required(CONF_CONFIG_JSON, default='BrematicPro.json'): str,
                vol.Required(CONF_ROOMS_JSON, default='BrematicProRooms.json'): str,
                vol.Optional('read_json', default=False): bool,
                vol.Optional('process_data', default=False): bool,
            }),
            errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Link the options flow for this integration."""
        return BrematicProOptionsFlow(config_entry)

class BrematicProOptionsFlow(config_entries.OptionsFlow):
    """Options flow for BrematicPro."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        context = self.context or {}
        return await BrematicProConfigFlow._common_flow_handler(self.hass, context, user_input)
