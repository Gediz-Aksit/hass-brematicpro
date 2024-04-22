from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_CONFIG_JSON
from .readconfigjson import read_and_transform_json

class BrematicProConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    # ... other methods ...

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
            return self.async_create_entry(title="", data={})

        config_json_filename = self.config_entry.data.get(CONF_CONFIG_JSON, 'DefaultFilename.json')

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional('reload', default=False): bool,
            }),
            description_placeholders={"filename": config_json_filename},
            errors=errors
        )
