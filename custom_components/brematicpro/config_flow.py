from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_CONFIG_JSON, CONF_ROOMS_JSON, CONF_INTERNAL_JSON

class BrematicProConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for BrematicPro."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            # Here, you should handle checking or preparation before creating the entry.
            return self.async_create_entry(title="BrematicPro", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SYSTEM_CODE, default='Enter your system code here'): str,
                vol.Required(CONF_CONFIG_JSON, default='BrematicPro.json'): str,
                vol.Required(CONF_ROOMS_JSON, default='BrematicProRooms.json'): str
            }),
            errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return BrematicProOptionsFlow(config_entry)

class BrematicProOptionsFlow(config_entries.OptionsFlow):
    """Options flow for BrematicPro."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        if user_input is not None:
            # Here you could handle updating internal JSON data or other settings
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional('update_data', default=False): bool
            }),
            errors=errors
        )
