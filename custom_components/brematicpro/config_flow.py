from homeassistant import config_entries, exceptions
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_CONFIG_JSON  # Import the constants

class BrematicProConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for BrematicPro."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            # Validate the filename
            valid = await self._validate_filename(user_input[CONF_CONFIG_JSON])
            if valid:
                return self.async_create_entry(title="BrematicPro", data=user_input)
            else:
                errors["base"] = "file_not_found"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SYSTEM_CODE): str,
                vol.Required(CONF_CONFIG_JSON): str
            }),
            errors=errors
        )

    async def _validate_filename(self, filename):
        """Validate the filename to check if file exists in HA directory."""
        file_path = self.hass.config.path(filename)
        try:
            with open(file_path, 'r') as file:
                # If necessary, add further file validation here
                return True
        except FileNotFoundError:
            return False
