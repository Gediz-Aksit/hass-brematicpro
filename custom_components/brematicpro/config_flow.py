from homeassistant import config_entries
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_CONFIG_JSON  

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
                vol.Required(CONF_SYSTEM_CODE): str,
                vol.Required(CONF_CONFIG_JSON, default='BrematicPro.json'): str
            }),
            errors=errors,
            description_placeholders={
                'system_code': 'System Code',  
                'config_json': 'Filename for configuration JSON'  
            }
        )

class BrematicProOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            await self.hass.async_add_executor_job(
                your_reload_function, self.hass, self.config_entry
            )
            return self.async_create_entry(title="", data=user_input)
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("reload", default=False): bool,
            }),
            description_placeholders={"reload": "Check to reload JSON"}
        )