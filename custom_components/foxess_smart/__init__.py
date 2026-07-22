"""FoxESS H12 Smart Integration."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .modbus_client import FoxESSModbusClient
from .coordinator import FoxESSUpdateCoordinator

PLATFORMS = ["sensor", "select"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up FoxESS H12 Smart from a config entry."""
    host = entry.data["host"]
    port = entry.data["port"]
    slave_id = entry.data["slave_id"]
    scan_interval = entry.data["scan_interval"]

    client = FoxESSModbusClient(host, port, slave_id)
    coordinator = FoxESSUpdateCoordinator(hass, client, scan_interval)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
