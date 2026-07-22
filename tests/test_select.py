import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

import tests.hass_mock

from custom_components.foxess_smart.const import DOMAIN, WORK_MODES
from custom_components.foxess_smart.select import FoxESSWorkModeSelect, async_setup_entry


class TestFoxESSWorkModeSelect(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.coordinator = MagicMock()
        self.coordinator.client.host = "192.168.1.100"
        self.coordinator.data = {"work_mode": 1}
        self.coordinator.hass = MagicMock()
        self.coordinator.async_request_refresh = AsyncMock()

    def test_init_and_properties(self):
        select = FoxESSWorkModeSelect(self.coordinator)
        self.assertEqual(select._attr_name, "FoxESS H12 Work Mode")
        self.assertEqual(
            select._attr_unique_id, "foxess_smart_work_mode_192.168.1.100"
        )
        self.assertEqual(select._attr_options, list(WORK_MODES.keys()))

    def test_current_option(self):
        select = FoxESSWorkModeSelect(self.coordinator)
        
        # Test mode 1 -> Self Use
        self.coordinator.data = {"work_mode": 1}
        self.assertEqual(select.current_option, "Self Use")

        # Test mode 2 -> Feed-in First
        self.coordinator.data = {"work_mode": 2}
        self.assertEqual(select.current_option, "Feed-in First")

        # Test mode 6 -> Force Charge
        self.coordinator.data = {"work_mode": 6}
        self.assertEqual(select.current_option, "Force Charge")

        # Test None data
        self.coordinator.data = None
        self.assertIsNone(select.current_option)

        # Test missing key or None value
        self.coordinator.data = {}
        self.assertIsNone(select.current_option)

    def test_device_info(self):
        select = FoxESSWorkModeSelect(self.coordinator)
        dev_info = select.device_info
        self.assertEqual(dev_info["name"], "FoxESS H12 Smart Inverter")
        self.assertEqual(dev_info["manufacturer"], "FoxESS")
        self.assertEqual(dev_info["model"], "H12 Smart")
        self.assertEqual(dev_info["identifiers"], {(DOMAIN, "192.168.1.100")})

    async def test_async_select_option(self):
        select = FoxESSWorkModeSelect(self.coordinator)
        
        # Mock async_add_executor_job to immediately call the passed function and args
        async def mock_add_executor_job(func, *args):
            return func(*args)

        self.coordinator.hass.async_add_executor_job = mock_add_executor_job

        await select.async_select_option("Backup")
        self.coordinator.client.write_work_mode.assert_called_once_with(3)
        self.coordinator.async_request_refresh.assert_called_once()

    async def test_async_setup_entry(self):
        hass = MagicMock()
        entry = MagicMock()
        entry.entry_id = "test_entry_123"
        hass.data = {DOMAIN: {entry.entry_id: self.coordinator}}
        async_add_entities = MagicMock()

        await async_setup_entry(hass, entry, async_add_entities)
        async_add_entities.assert_called_once()
        entities = async_add_entities.call_args[0][0]
        self.assertEqual(len(entities), 1)
        self.assertIsInstance(entities[0], FoxESSWorkModeSelect)


if __name__ == "__main__":
    unittest.main()
