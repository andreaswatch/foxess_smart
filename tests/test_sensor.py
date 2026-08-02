import unittest
from unittest.mock import MagicMock

import tests.hass_mock

from custom_components.foxess_smart.sensor import SENSOR_TYPES, FoxESSSensor


class TestFoxESSSensor(unittest.TestCase):
    def test_sensor_types_count(self):
        # 28 direct Modbus register sensors + 4 derived unidirectional power sensors + 1 total PV power sensor = 33
        self.assertEqual(len(SENSOR_TYPES), 33)

    def test_sensor_entity_properties(self):
        mock_coordinator = MagicMock()
        mock_coordinator.client.host = "192.168.1.100"
        mock_coordinator.data = {
            "pv1_voltage": 350.0,
            "grid_ct_power": 3.905,
            "grid_import_power": 0.0,
            "grid_export_power": 3.905,
        }

        pv1_info = SENSOR_TYPES["pv1_voltage"]
        sensor = FoxESSSensor(mock_coordinator, "pv1_voltage", pv1_info)

        self.assertEqual(sensor._attr_name, "PV1 Voltage")
        self.assertEqual(
            sensor._attr_unique_id, "foxess_smart_pv1_voltage_192.168.1.100"
        )
        self.assertTrue(sensor._attr_has_entity_name)
        from homeassistant.const import EntityCategory
        self.assertEqual(sensor._attr_entity_category, EntityCategory.DIAGNOSTIC)
        self.assertEqual(sensor.native_value, 350.0)

        dev_info = sensor.device_info
        self.assertEqual(dev_info["name"], "FoxESS H12 Smart Inverter")
        self.assertEqual(dev_info["manufacturer"], "FoxESS")
        self.assertEqual(dev_info["model"], "H12 Smart")

    def test_sensor_none_data(self):
        mock_coordinator = MagicMock()
        mock_coordinator.data = None
        pv1_info = SENSOR_TYPES["pv1_voltage"]
        sensor = FoxESSSensor(mock_coordinator, "pv1_voltage", pv1_info)
        self.assertIsNone(sensor.native_value)

    def test_integral_sensor_init_and_restore(self):
        from custom_components.foxess_smart.sensor import FoxESSEnergyIntegralSensor
        mock_coordinator = MagicMock()
        mock_coordinator.client.host = "192.168.1.100"
        sensor = FoxESSEnergyIntegralSensor(mock_coordinator, "grid_import_power", "Grid Import Energy")
        
        self.assertEqual(sensor._attr_name, "Grid Import Energy")
        self.assertEqual(sensor._attr_unique_id, "foxess_smart_grid_import_power_integral_192.168.1.100")
        self.assertTrue(sensor._attr_has_entity_name)
        self.assertEqual(sensor.native_value, 0.0)

from unittest.mock import AsyncMock

class TestFoxESSIntegralSensorAsync(unittest.IsolatedAsyncioTestCase):
    async def test_async_added_to_hass_restores_state(self):
        from custom_components.foxess_smart.sensor import FoxESSEnergyIntegralSensor
        mock_coordinator = MagicMock()
        sensor = FoxESSEnergyIntegralSensor(mock_coordinator, "grid_import_power", "Grid Import Energy")
        
        mock_state = MagicMock()
        mock_state.native_value = "123.456"
        sensor.async_get_last_sensor_data = AsyncMock(return_value=mock_state)
        
        await sensor.async_added_to_hass()
        self.assertEqual(sensor.native_value, 123.456)

    async def test_async_added_to_hass_corrupt_or_none(self):
        from custom_components.foxess_smart.sensor import FoxESSEnergyIntegralSensor
        mock_coordinator = MagicMock()
        sensor = FoxESSEnergyIntegralSensor(mock_coordinator, "grid_import_power", "Grid Import Energy")
        
        # Test invalid string
        mock_state = MagicMock()
        mock_state.native_value = "invalid"
        sensor.async_get_last_sensor_data = AsyncMock(return_value=mock_state)
        
        await sensor.async_added_to_hass()
        self.assertEqual(sensor.native_value, 0.0)

    def test_riemann_integration_calculation(self):
        from custom_components.foxess_smart.sensor import FoxESSEnergyIntegralSensor
        from datetime import datetime, timezone, timedelta
        import tests.hass_mock as hass_mock

        t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        t1 = t0 + timedelta(seconds=180)  # 0.05 hours -> 4.0 kW * 0.05 h = 0.2 kWh

        times = [t0, t1]
        hass_mock.util_dt_mock.utcnow.side_effect = lambda: times.pop(0) if times else t1

        mock_coordinator = MagicMock()
        sensor = FoxESSEnergyIntegralSensor(mock_coordinator, "grid_import_power", "Grid Import Energy")
        mock_coordinator.data = {"grid_import_power": 4.0}

        try:
            sensor._handle_coordinator_update()
            self.assertEqual(sensor.native_value, 0.0)

            sensor._handle_coordinator_update()
            self.assertEqual(sensor.native_value, 0.2)
        finally:
            hass_mock.util_dt_mock.utcnow.side_effect = lambda: datetime.now(timezone.utc)


if __name__ == "__main__":
    unittest.main()







