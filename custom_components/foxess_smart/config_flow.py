"""Config flow for FoxESS H12 Smart integration."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .modbus_client import FoxESSModbusClient

DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host", default="192.168.178.194"): str,
        vol.Required("port", default=502): int,
        vol.Required("slave_id", default=247): int,
        vol.Required("scan_interval", default=15): int,
    }
)


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
                )
                if success:
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

    def _test_connection(self, host: str, port: int, slave: int) -> bool:
        """Test modbus connection by reading holding register 49203."""
        client = FoxESSModbusClient(host, port, slave)
        # Attempt to read work mode register as a test
        regs = client.read_registers(49203, 1)
        if not regs:
            raise Exception("No registers returned by inverter.")
        return True
