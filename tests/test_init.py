import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import tests.hass_mock

from custom_components.foxess_smart import (
    DOMAIN,
    PLATFORMS,
    async_setup_entry,
    async_unload_entry,
    async_reload_entry,
)


class TestInit(unittest.IsolatedAsyncioTestCase):
    async def test_async_setup_entry(self):
        hass = MagicMock()
        hass.data = {}
        hass.config_entries.async_forward_entry_setups = AsyncMock()

        entry = MagicMock()
        entry.entry_id = "test_entry_123"
        entry.options = {}
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

    async def test_async_reload_entry_no_coordinator(self):
        hass = MagicMock()
        hass.data = {}
        hass.config_entries.async_reload = AsyncMock()

        entry = MagicMock()
        entry.entry_id = "test_entry_123"

        await async_reload_entry(hass, entry)
        hass.config_entries.async_reload.assert_called_once_with("test_entry_123")

    async def test_async_reload_entry_no_change(self):
        from datetime import timedelta
        hass = MagicMock()
        hass.config_entries.async_reload = AsyncMock()

        mock_coordinator = MagicMock()
        mock_coordinator.client.host = "192.168.1.100"
        mock_coordinator.client.port = 502
        mock_coordinator.client.slave = 1
        mock_coordinator.client.timeout = 3
        mock_coordinator.update_interval = timedelta(seconds=10)

        hass.data = {DOMAIN: {"test_entry_123": mock_coordinator}}

        entry = MagicMock()
        entry.entry_id = "test_entry_123"
        entry.data = {
            "host": "192.168.1.100",
            "port": 502,
            "slave_id": 1,
            "scan_interval": 10,
            "timeout": 3,
        }
        entry.options = {}

        await async_reload_entry(hass, entry)
        hass.config_entries.async_reload.assert_not_called()

    async def test_async_reload_entry_connection_changed(self):
        from datetime import timedelta
        hass = MagicMock()
        hass.config_entries.async_reload = AsyncMock()

        mock_coordinator = MagicMock()
        mock_coordinator.client.host = "192.168.1.100"
        mock_coordinator.client.port = 502
        mock_coordinator.client.slave = 1
        mock_coordinator.client.timeout = 3
        mock_coordinator.update_interval = timedelta(seconds=10)

        hass.data = {DOMAIN: {"test_entry_123": mock_coordinator}}

        entry = MagicMock()
        entry.entry_id = "test_entry_123"
        entry.data = {
            "host": "192.168.1.200",  # Changed!
            "port": 502,
            "slave_id": 1,
            "scan_interval": 10,
            "timeout": 3,
        }
        entry.options = {}

        await async_reload_entry(hass, entry)
        hass.config_entries.async_reload.assert_called_once_with("test_entry_123")

    async def test_async_reload_entry_setup_energy_true(self):
        from datetime import timedelta
        hass = MagicMock()
        hass.config_entries.async_reload = AsyncMock()

        mock_coordinator = MagicMock()
        mock_coordinator.client.host = "192.168.1.100"
        mock_coordinator.client.port = 502
        mock_coordinator.client.slave = 1
        mock_coordinator.client.timeout = 3
        mock_coordinator.update_interval = timedelta(seconds=10)

        hass.data = {DOMAIN: {"test_entry_123": mock_coordinator}}

        entry = MagicMock()
        entry.entry_id = "test_entry_123"
        entry.data = {
            "host": "192.168.1.100",
            "port": 502,
            "slave_id": 1,
            "scan_interval": 10,
            "timeout": 3,
        }
        entry.options = {"setup_energy": True}  # Setup energy requested

        await async_reload_entry(hass, entry)
        hass.config_entries.async_reload.assert_called_once_with("test_entry_123")

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
