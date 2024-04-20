import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_TOKEN

from .const import DOMAIN

class SimpleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example simple config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="Simple Device", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
            vol.Required(CONF_SYSTEM_CODE): vol.Schema(str, description="Enter your system code"),
            vol.Required(CONF_CONFIG_JSON): vol.Schema(str, description="Enter your configuration JSON")
            }),
            errors=errors
        )
