import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_CONFIG_JSON, CONF_ROOMS_JSON
from .readconfigjson import read_and_transform_json, setup_entry_components

class BrematicProConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for BrematicPro."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}
        if user_input is not None:
            if user_input.get('read_json'):
                # Assuming entry is already available via self.hass.config_entries
                entry = await self.async_set_unique_id(DOMAIN)
                await self.hass.async_add_executor_job(
                    read_and_transform_json,
                    self.hass,
                    entry,
                    user_input[CONF_CONFIG_JSON],
                    user_input.get(CONF_ROOMS_JSON)
                )
            if user_input.get('process_data'):
                entry = await self.async_set_unique_id(DOMAIN)
                await setup_entry_components(self.hass, entry)
            
            # Save the entered data as configuration
            self.hass.config_entries.async_update_entry(entry, data=user_input)
            return self.async_create_entry(title="BrematicPro", data=user_input)

        # Default values for the form
        data_schema = vol.Schema({
            vol.Required(CONF_SYSTEM_CODE): str,
            vol.Required(CONF_CONFIG_JSON, default="BrematicPro.json"): str,
            vol.Optional(CONF_ROOMS_JSON, default="BrematicProRooms.json"): str,
            vol.Optional('read_json', default=False): bool,
            vol.Optional('process_data', default=False): bool,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors,
            description_placeholders={
                "download_url": "/api/brematicpro/download_json"
            }
        )

    async def async_step_import(self, user_input):
        """Handle the initial step."""
        return await self.async_step_user(user_input)

    @staticmethod
    def async_get_options_flow(config_entry):
        return BrematicProOptionsFlow(config_entry)

class BrematicProOptionsFlow(config_entries.OptionsFlow):
    """Options flow for BrematicPro."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await BrematicProConfigFlow.async_step_user(None, user_input)
