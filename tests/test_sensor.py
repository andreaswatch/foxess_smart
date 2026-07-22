import sys
import unittest
from unittest.mock import MagicMock

# Mock homeassistant modules before importing custom components
class MockSensorEntity:
    pass


class MockCoordinatorEntity:
    def __init__(self, coordinator):
        self.coordinator = coordinator


mock_ha = MagicMock()
sys.modules["homeassistant"] = mock_ha
sys.modules["homeassistant.components"] = MagicMock()
sys.modules["homeassistant.components.sensor"] = MagicMock(
    SensorEntity=MockSensorEntity,
    SensorDeviceClass=MagicMock(),
    SensorStateClass=MagicMock(),
)
sys.modules["homeassistant.const"] = MagicMock()
sys.modules["homeassistant.helpers"] = MagicMock()
sys.modules["homeassistant.helpers.update_coordinator"] = MagicMock(
    CoordinatorEntity=MockCoordinatorEntity
)

from custom_components.foxess_smart.sensor import SENSOR_TYPES, FoxESSSensor


class TestFoxESSSensor(unittest.TestCase):
    def test_sensor_types_count(self):
        # 28 direct Modbus register sensors + 4 derived unidirectional power sensors = 32
        self.assertEqual(len(SENSOR_TYPES), 32)

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

        self.assertEqual(sensor._attr_name, "FoxESS H12 PV1 Voltage")
        self.assertEqual(
            sensor._attr_unique_id, "foxess_smart_pv1_voltage_192.168.1.100"
        )
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


if __name__ == "__main__":
    unittest.main()
