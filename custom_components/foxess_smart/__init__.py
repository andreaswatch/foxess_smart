"""FoxESS H12 Smart Integration."""
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .modbus_client import FoxESSModbusClient
from .coordinator import FoxESSUpdateCoordinator
from .energy_dashboard import async_setup_energy_dashboard

PLATFORMS = ["sensor", "select", "number"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up FoxESS H12 Smart from a config entry."""
    host = entry.options.get("host", entry.data["host"])
    port = entry.options.get("port", entry.data["port"])
    slave_id = entry.options.get("slave_id", entry.data["slave_id"])
    scan_interval = entry.options.get("scan_interval", entry.data["scan_interval"])
    timeout = entry.options.get("timeout", entry.data.get("timeout", 3))

    client = FoxESSModbusClient(host, port, slave_id, timeout)
    coordinator = FoxESSUpdateCoordinator(hass, client, scan_interval)
    coordinator.entry_id = entry.entry_id

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register service to return all values
    async def get_all_values(call: ServiceCall) -> dict:
        """Service to return all values as JSON."""
        response = {}
        if DOMAIN in hass.data:
            for _, coord in hass.data[DOMAIN].items():
                if hasattr(coord, "data") and coord.data:
                    response[coord.client.host] = coord.data
        return response
        
    if not hass.services.has_service(DOMAIN, "get_all_values"):
        hass.services.async_register(
            DOMAIN,
            "get_all_values",
            get_all_values,
            supports_response=SupportsResponse.ONLY,
        )
    
    # Configure Energy Dashboard if requested
    setup_energy = entry.options.get("setup_energy", entry.data.get("setup_energy", False))
    if setup_energy:
        hass.async_create_task(async_setup_energy_dashboard(hass, entry))
    
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    return True

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
