import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_SYSTEM_CODE, CONF_CONFIG_JSON, CONF_ROOMS_JSON
from .readconfigjson import read_and_transform_json, setup_entry_components

async def setup_user_config(hass: core.HomeAssistant, config: dict):
    """Setup configuration that might be adjusted by the user at runtime."""
    # Here you could initialize or adjust services based on user configuration
    hass.data[DOMAIN]['runtime_config'] = config

class BrematicProConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for BrematicPro."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle a user flow initiated by the user."""
        errors = {}
        if user_input is not None:
            # Process user input here
            if user_input.get('read_json'):
                entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
                await self.hass.async_add_executor_job(
                    read_and_transform_json,
                    self.hass,
                    entry,
                    user_input[CONF_CONFIG_JSON],
                    user_input.get(CONF_ROOMS_JSON)
                )
            if user_input.get('process_data'):
                entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
                await setup_entry_components(self.hass, entry)

            # Save the entered data as configuration
            await self.async_set_unique_id(DOMAIN)
            self.hass.config_entries.async_update_entry(entry, data=user_input)
            return self.async_create_entry(title="BrematicPro", data=user_input)

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

