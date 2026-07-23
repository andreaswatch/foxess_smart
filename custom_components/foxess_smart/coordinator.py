"""Data update coordinator for FoxESS H12 Smart inverter."""

from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)


from .modbus_client import (
    FoxESSModbusClient,
    decode_s16,
    decode_u32_be,
    decode_s32_be,
    decode_u32_le,
)

_LOGGER = logging.getLogger(__name__)


class FoxESSUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching FoxESS inverter data via Modbus TCP."""

    def __init__(self, hass, client: FoxESSModbusClient, scan_interval: int):
        """Initialize the coordinator."""
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name="FoxESS Update Coordinator",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self):
        """Fetch data from inverter via executor."""
        try:
            return await self.hass.async_add_executor_job(self._poll_inverter)
        except Exception as ex:
            raise UpdateFailed(f"Error communicating with FoxESS H12: {ex}")

    def _poll_inverter(self) -> dict:
        """Perform 11 sequential block reads from Modbus registers."""
        data = {}

        # Block 1: BMS1 Info (37609 - 37612)
        bms1 = self.client.read_registers(37609, 4)
        data["battery_voltage"] = round(bms1[0] * 0.1, 1)
        data["battery_current"] = round(decode_s16(bms1[1]) * 0.1, 1)
        data["battery_temp"] = round(decode_s16(bms1[2]) * 0.1, 1)
        data["battery_soc"] = bms1[3]

        # Block 2: BMS2 Info (38310)
        bms2 = self.client.read_registers(38310, 1)
        data["battery_bms2_soc"] = bms2[0]

        # Block 3: PV Voltages/Currents (39070 - 39073)
        pv_vi = self.client.read_registers(39070, 4)
        data["pv1_voltage"] = round(pv_vi[0] * 0.1, 1)
        data["pv1_current"] = round(pv_vi[1] * 0.01, 2)
        data["pv2_voltage"] = round(pv_vi[2] * 0.1, 1)
        data["pv2_current"] = round(pv_vi[3] * 0.01, 2)

        # Block 4: Grid Voltages/Currents (39123 - 39131)
        grid_vi = self.client.read_registers(39123, 9)
        data["grid_voltage_r"] = round(grid_vi[0] * 0.1, 1)
        data["grid_voltage_s"] = round(grid_vi[1] * 0.1, 1)
        data["grid_voltage_t"] = round(grid_vi[2] * 0.1, 1)
        data["grid_current_r"] = round(decode_s32_be(grid_vi[3:5]) * 0.001, 3)
        data["grid_current_s"] = round(decode_s32_be(grid_vi[5:7]) * 0.001, 3)
        data["grid_current_t"] = round(decode_s32_be(grid_vi[7:9]) * 0.001, 3)

        # Block 5: Grid CT Power (39168 - 39169)
        grid_ct = self.client.read_registers(39168, 2)
        grid_ct_val = round(decode_s32_be(grid_ct) * 0.001, 3)  # W -> kW
        data["grid_ct_power"] = grid_ct_val
        data["grid_import_power"] = round(max(0.0, -grid_ct_val), 3)
        data["grid_export_power"] = round(max(0.0, grid_ct_val), 3)

        # Block 6: Load Power (39219 - 39226)
        load_p = self.client.read_registers(39219, 8)
        data["load_power_r"] = round(decode_s32_be(load_p[0:2]) * 0.001, 3)
        data["load_power_s"] = round(decode_s32_be(load_p[2:4]) * 0.001, 3)
        data["load_power_t"] = round(decode_s32_be(load_p[4:6]) * 0.001, 3)
        data["load_power_total"] = round(decode_s32_be(load_p[6:8]) * 0.001, 3)

        # Block 7: Battery Combined Power (39237 - 39238)
        bat_p = self.client.read_registers(39237, 2)
        bat_p_val = round(decode_s32_be(bat_p) * 0.001, 3)  # W -> kW
        data["battery_combined_power"] = bat_p_val
        data["battery_charge_power"] = round(max(0.0, -bat_p_val), 3)
        data["battery_discharge_power"] = round(max(0.0, bat_p_val), 3)

        # Block 8: Grid Power (39248 - 39253)
        grid_p = self.client.read_registers(39248, 6)
        data["grid_power_r"] = round(decode_s32_be(grid_p[0:2]) * 0.001, 3)
        data["grid_power_s"] = round(decode_s32_be(grid_p[2:4]) * 0.001, 3)
        data["grid_power_t"] = round(decode_s32_be(grid_p[4:6]) * 0.001, 3)

        # Block 9: PV Power (39279 - 39282)
        pv_p = self.client.read_registers(39279, 4)
        data["pv1_power"] = round(decode_s32_be(pv_p[0:2]) * 0.001, 3)
        data["pv2_power"] = round(decode_s32_be(pv_p[2:4]) * 0.001, 3)
        data["pv_power_total"] = round(data["pv1_power"] + data["pv2_power"], 3)

        # Block 10: PV Energy (39602 - 39605)
        pv_e = self.client.read_registers(39602, 4)
        data["pv_production_total"] = round(decode_u32_le(pv_e[0:2]) * 0.1, 1)
        data["pv_production_today"] = round(decode_u32_le(pv_e[2:4]) * 0.1, 1)

        # Block 11: Work Mode (49203)
        mode = self.client.read_registers(49203, 1)
        data["work_mode"] = mode[0]

        return data
