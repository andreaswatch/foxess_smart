import unittest
from unittest.mock import MagicMock

import tests.hass_mock

from custom_components.foxess_smart.coordinator import FoxESSUpdateCoordinator
from custom_components.foxess_smart.modbus_client import (
    decode_s16,
    decode_u32_be,
    decode_s32_be,
    decode_u32_le,
)


class TestCoordinatorParsing(unittest.TestCase):
    def test_derived_power_calculations(self):
        # Grid CT Power: +3905 W (export)
        grid_ct_export = 3905 / 1000.0  # 3.905 kW
        grid_import = max(0.0, -grid_ct_export)
        grid_export = max(0.0, grid_ct_export)
        self.assertEqual(grid_import, 0.0)
        self.assertEqual(grid_export, 3.905)

        # Grid CT Power: -1500 W (import)
        grid_ct_import = -1500 / 1000.0  # -1.500 kW
        grid_import2 = max(0.0, -grid_ct_import)
        grid_export2 = max(0.0, grid_ct_import)
        self.assertEqual(grid_import2, 1.5)
        self.assertEqual(grid_export2, 0.0)

        # Battery Combined Power: -2000 W (charging)
        bat_power_charge = -2000 / 1000.0  # -2.0 kW
        charge_power = max(0.0, -bat_power_charge)
        discharge_power = max(0.0, bat_power_charge)
        self.assertEqual(charge_power, 2.0)
        self.assertEqual(discharge_power, 0.0)

        # Battery Combined Power: 1000 W (discharging)
        bat_power_discharge = 1000 / 1000.0  # 1.0 kW
        charge_power2 = max(0.0, -bat_power_discharge)
        discharge_power2 = max(0.0, bat_power_discharge)
        self.assertEqual(charge_power2, 0.0)
        self.assertEqual(discharge_power2, 1.0)

    def test_coordinator_poll_inverter(self):
        self.assertIsNotNone(
            FoxESSUpdateCoordinator, "FoxESSUpdateCoordinator must be defined"
        )
        mock_client = MagicMock()

        # Map block register addresses to mock returned register arrays
        def mock_read_registers(address, count):
            mapping = {
                37609: [520, 65516, 250, 85],
                38310: [86],
                39070: [3500, 1050, 3600, 800],
                39123: [2300, 2310, 2290, 0, 5000, 0, 5100, 0, 4900],
                39168: [0, 3905],
                39219: [0, 1000, 0, 1100, 0, 900, 0, 3000],
                39237: [65535, 63536],
                39248: [0, 1300, 0, 1300, 0, 1305],
                39279: [0, 36750, 0, 28800],
                39602: [0, 12345, 0, 250],
                49203: [1],
            }
            if address in mapping:
                return mapping[address]
            raise ValueError(f"Unexpected register read: {address}")

        mock_client.read_registers.side_effect = mock_read_registers

        coordinator = FoxESSUpdateCoordinator(
            hass=MagicMock(), client=mock_client, scan_interval=10
        )
        data = coordinator._poll_inverter()

        self.assertEqual(data["battery_voltage"], 52.0)
        self.assertEqual(data["battery_current"], -2.0)
        self.assertEqual(data["battery_temp"], 25.0)
        self.assertEqual(data["battery_soc"], 85)
        self.assertEqual(data["battery_bms2_soc"], 86)
        self.assertEqual(data["pv1_voltage"], 350.0)
        self.assertEqual(data["pv1_current"], 10.5)
        self.assertEqual(data["pv2_voltage"], 360.0)
        self.assertEqual(data["pv2_current"], 8.0)
        self.assertEqual(data["grid_voltage_r"], 230.0)
        self.assertEqual(data["grid_voltage_s"], 231.0)
        self.assertEqual(data["grid_voltage_t"], 229.0)
        self.assertEqual(data["grid_current_r"], 5.0)
        self.assertEqual(data["grid_current_s"], 5.1)
        self.assertEqual(data["grid_current_t"], 4.9)
        self.assertEqual(data["grid_ct_power"], 3.905)
        self.assertEqual(data["grid_import_power"], 0.0)
        self.assertEqual(data["grid_export_power"], 3.905)
        self.assertEqual(data["load_power_r"], 1.0)
        self.assertEqual(data["load_power_s"], 1.1)
        self.assertEqual(data["load_power_t"], 0.9)
        self.assertEqual(data["load_power_total"], 3.0)
        self.assertEqual(data["battery_combined_power"], -2.0)
        self.assertEqual(data["battery_charge_power"], 2.0)
        self.assertEqual(data["battery_discharge_power"], 0.0)
        self.assertEqual(data["grid_power_r"], 1.3)
        self.assertEqual(data["grid_power_s"], 1.3)
        self.assertEqual(data["grid_power_t"], 1.305)
        self.assertEqual(data["pv1_power"], 3.675)
        self.assertEqual(data["pv2_power"], 2.88)
        self.assertEqual(data["pv_power_total"], 6.555)
        self.assertEqual(data["pv_production_total"], 1234.5)
        self.assertEqual(data["pv_production_today"], 25.0)
        self.assertEqual(data["work_mode"], 1)


if __name__ == "__main__":
    unittest.main()
