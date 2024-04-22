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
            config_data = {
                CONF_SYSTEM_CODE: user_input[CONF_SYSTEM_CODE],
                CONF_CONFIG_JSON: user_input[CONF_CONFIG_JSON]
            }
            return self.async_create_entry(title="BrematicPro", data=config_data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SYSTEM_CODE): str,
                vol.Required(CONF_CONFIG_JSON, default='BrematicPro.json'): str
            }),
            errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Link to the options flow for this integration."""
        return BrematicProOptionsFlow(config_entry)

class BrematicProOptionsFlow(config_entries.OptionsFlow):
    """Options flow for BrematicPro."""
    
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        if user_input is not None and user_input.get('reload', False):
            # Reload the configuration from the file
            await self.hass.async_add_executor_job(
                read_and_transform_json, self.hass, self.config_entry
            )
            # No need to create an entry for options, just end the flow
            return self.async_abort(reason="configuration_reloaded")

        config_json_filename = self.config_entry.data.get(CONF_CONFIG_JSON, 'DefaultFilename.json')

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional('reload', default=False): bool,
            }),
            description_placeholders={"filename": config_json_filename},
            errors=errors
        )
