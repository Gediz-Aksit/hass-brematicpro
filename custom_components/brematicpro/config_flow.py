import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_CONFIG_JSON  # ensure these are defined in your const.py

class BrematicProConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for BrematicPro."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            # Here, add your validation logic
            return self.async_create_entry(title="BrematicPro", data=user_input)

        # Update your schema to include descriptions
        data_schema = vol.Schema({
            vol.Required(CONF_SYSTEM_CODE, description={"suggested_value": "Your system code"}): str,
            vol.Required(CONF_CONFIG_JSON, description={"suggested_value": "Filename for configuration JSON"}): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

