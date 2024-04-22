from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_CONFIG_JSON
from .readconfigjson import read_and_transform_json

class BrematicProConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for BrematicPro."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="BrematicPro", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SYSTEM_CODE, description={"suggested_value": "Enter system code"}): str,
                vol.Required(CONF_CONFIG_JSON, description={"suggested_value": "BrematicPro.json"}): str
            }),
            description_placeholders={
                'system_code_description': 'Please enter the system code for your BrematicPro device.',
                'config_json_description': f'Enter the configuration file name. Default is "BrematicPro.json".'
            },
            errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return BrematicProOptionsFlow(config_entry)

class BrematicProOptionsFlow(config_entries.OptionsFlow):
    """Options flow for BrematicPro."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        if user_input is not None and user_input.get('reload', False):
            await self.hass.async_add_executor_job(
                read_and_transform_json, self.hass, self.config_entry
            )
            return self.async_create_entry(title="", data={})

        config_json_filename = self.config_entry.data.get(CONF_CONFIG_JSON, 'DefaultFilename.json')

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional('reload', default=False): bool
            }),
            description_placeholders={"filename": f"Current configuration file: {config_json_filename}. Reload configuration now?"},
            errors=errors
        )
