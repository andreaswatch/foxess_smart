import unittest
from unittest.mock import MagicMock

import tests.hass_mock

from custom_components.foxess_smart.sensor import SENSOR_TYPES, FoxESSSensor


class TestFoxESSSensor(unittest.TestCase):
    def test_sensor_types_count(self):
        # 28 direct Modbus register sensors + 4 derived unidirectional power sensors
        # + 1 total PV power sensor + 6 native energy accumulator sensors = 39 ... but we expose 37
        self.assertEqual(len(SENSOR_TYPES), 37)

    def test_sensor_entity_properties(self):
        mock_coordinator = MagicMock()
        mock_coordinator.entry_id = "192.168.1.100"
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

        dev_info = sensor._attr_device_info
        self.assertEqual(dev_info["name"], "FoxESS H12 Smart Inverter")
        self.assertEqual(dev_info["manufacturer"], "andreaswatch")
        self.assertEqual(dev_info["model"], "H12 Smart")

    def test_sensor_none_data(self):
        mock_coordinator = MagicMock()
        mock_coordinator.entry_id = "192.168.1.100"
        mock_coordinator.data = None
        pv1_info = SENSOR_TYPES["pv1_voltage"]
        sensor = FoxESSSensor(mock_coordinator, "pv1_voltage", pv1_info)
        self.assertIsNone(sensor.native_value)


if __name__ == "__main__":
    unittest.main()







