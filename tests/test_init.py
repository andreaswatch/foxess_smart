import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Mock homeassistant modules before importing custom components
sys.modules["homeassistant"] = MagicMock()
sys.modules["homeassistant.core"] = MagicMock()
sys.modules["homeassistant.config_entries"] = MagicMock()
sys.modules["homeassistant.helpers"] = MagicMock()
sys.modules["homeassistant.helpers.update_coordinator"] = MagicMock()

from custom_components.foxess_smart import (
    DOMAIN,
    PLATFORMS,
    async_setup_entry,
    async_unload_entry,
)


class TestInit(unittest.IsolatedAsyncioTestCase):
    async def test_async_setup_entry(self):
        hass = MagicMock()
        hass.data = {}
        hass.config_entries.async_forward_entry_setups = AsyncMock()

        entry = MagicMock()
        entry.entry_id = "test_entry_123"
        entry.data = {
            "host": "192.168.1.100",
            "port": 502,
            "slave_id": 1,
            "scan_interval": 10,
        }

        with patch(
            "custom_components.foxess_smart.coordinator.FoxESSUpdateCoordinator.async_config_entry_first_refresh",
            new_callable=AsyncMock,
        ) as mock_refresh:
            result = await async_setup_entry(hass, entry)

            self.assertTrue(result)
            self.assertIn(DOMAIN, hass.data)
            self.assertIn(entry.entry_id, hass.data[DOMAIN])
            mock_refresh.assert_called_once()
            hass.config_entries.async_forward_entry_setups.assert_called_once_with(
                entry, PLATFORMS
            )

    async def test_async_unload_entry_success(self):
        hass = MagicMock()
        hass.data = {DOMAIN: {"test_entry_123": MagicMock()}}
        hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

        entry = MagicMock()
        entry.entry_id = "test_entry_123"

        result = await async_unload_entry(hass, entry)

        self.assertTrue(result)
        self.assertNotIn("test_entry_123", hass.data[DOMAIN])
        hass.config_entries.async_unload_platforms.assert_called_once_with(
            entry, PLATFORMS
        )

    async def test_async_unload_entry_failure(self):
        hass = MagicMock()
        mock_coordinator = MagicMock()
        hass.data = {DOMAIN: {"test_entry_123": mock_coordinator}}
        hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)

        entry = MagicMock()
        entry.entry_id = "test_entry_123"

        result = await async_unload_entry(hass, entry)

        self.assertFalse(result)
        self.assertIn("test_entry_123", hass.data[DOMAIN])


if __name__ == "__main__":
    unittest.main()
