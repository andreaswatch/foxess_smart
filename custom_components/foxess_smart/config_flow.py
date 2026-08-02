"""Config flow for FoxESS H12 Smart integration."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .modbus_client import FoxESSModbusClient

def get_schema(data=None):
    if data is None:
        data = {}
    return vol.Schema(
        {
            vol.Required("host", default=data.get("host", "192.168.178.194")): str,
            vol.Required("port", default=data.get("port", 502)): int,
            vol.Required("slave_id", default=data.get("slave_id", 247)): int,
            vol.Required("scan_interval", default=data.get("scan_interval", 15)): int,
            vol.Required("timeout", default=data.get("timeout", 3)): int,
            vol.Optional("setup_energy", default=data.get("setup_energy", False)): bool,
            vol.Optional("energy_import_price", default=data.get("energy_import_price", 0.0)): vol.Coerce(float),
            vol.Optional("energy_export_price", default=data.get("energy_export_price", 0.0)): vol.Coerce(float),
        }
    )

DATA_SCHEMA = get_schema()


class FoxESSSmartConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FoxESS H12 Smart."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        description_placeholders = {}
        if user_input is not None:
            # Validate connection in executor
            try:
                success = await self.hass.async_add_executor_job(
                    self._test_connection,
                    user_input["host"],
                    user_input["port"],
                    user_input["slave_id"],
                    user_input.get("timeout", 3),
                )
                if success:
                    await self.async_set_unique_id(user_input["host"])
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"FoxESS H12 Smart ({user_input['host']})",
                        data=user_input,
                    )
            except Exception as e:
                errors["base"] = "connection_error"
                description_placeholders = {"error_details": str(e)}

        return self.async_show_form(
            step_id="user", 
            data_schema=DATA_SCHEMA, 
            errors=errors,
            description_placeholders=description_placeholders
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return FoxESSSmartOptionsFlowHandler()

    def _test_connection(self, host: str, port: int, slave: int, timeout: int = 3) -> bool:
        """Test modbus connection by reading holding register 49203."""
        client = FoxESSModbusClient(host, port, slave, timeout)
        # Attempt to read work mode register as a test
        regs = client.read_registers(49203, 1)
        if not regs:
            raise Exception("No registers returned by inverter.")
        return True

class FoxESSSmartOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for FoxESS H12 Smart."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Merge data and options
        data = dict(self.config_entry.data)
        data.update(self.config_entry.options)
        
        return self.async_show_form(
            step_id="init",
            data_schema=get_schema(data)
        )
