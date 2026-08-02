from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import entity_registry as er
from homeassistant.components.energy.data import (
    async_get_manager,
    EnergyPreferencesUpdate,
    SolarSourceType,
    BatterySourceType,
    GridSourceType,
    FlowFromGridSourceType,
    FlowToGridSourceType,
)
import logging
import asyncio
from homeassistant.components import persistent_notification

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN

async def async_setup_energy_dashboard(hass: HomeAssistant, entry: ConfigEntry):
    """Programmatically configure the Energy Dashboard by replacing existing setup."""
    
    # We delay slightly to ensure the entity registry has fully committed the new entities.
    await asyncio.sleep(10)
    
    manager = await async_get_manager(hass)
    registry = er.async_get(hass)
    
    def get_entity_id(unique_id: str) -> str | None:
        """Lookup entity ID by its unique ID in the registry."""
        return registry.async_get_entity_id("sensor", DOMAIN, unique_id)
        
    # Get entity IDs using their precise unique_ids
    grid_import = get_entity_id(f"foxess_smart_grid_import_total_{entry.entry_id}")
    grid_export = get_entity_id(f"foxess_smart_grid_export_total_{entry.entry_id}")
    battery_charge = get_entity_id(f"foxess_smart_battery_charge_total_{entry.entry_id}")
    battery_discharge = get_entity_id(f"foxess_smart_battery_discharge_total_{entry.entry_id}")
    solar_yield = get_entity_id(f"foxess_smart_pv_production_total_{entry.entry_id}")
    
    missing = []
    if not grid_import: missing.append("Grid Import")
    if not grid_export: missing.append("Grid Export")
    if not battery_charge: missing.append("Battery Charge")
    if not battery_discharge: missing.append("Battery Discharge")
    if not solar_yield: missing.append("Solar Yield")
    
    if missing:
        msg = f"FoxESS Energy Dashboard Setup aborted: Could not find entity IDs for {missing}."
        _LOGGER.warning(msg)
        persistent_notification.async_create(
            hass, msg, title="FoxESS Smart - Setup Failed"
        )
        return
        
    _LOGGER.info("Setting up Energy Dashboard with FoxESS Smart sensors. (Replacing existing setup)")
    
    # We replace the energy preferences exactly as requested by the user
    energy_prefs = EnergyPreferencesUpdate(energy_sources=[]) # type: ignore
    
    # Add Solar Source
    energy_prefs["energy_sources"].append(
        SolarSourceType(
            type="solar",
            stat_energy_from=solar_yield,
            config_entry_solar_forecast=None,
        )
    )
    
    # Add Battery Source
    energy_prefs["energy_sources"].append(
        BatterySourceType(
            type="battery",
            stat_energy_to=battery_charge,
            stat_energy_from=battery_discharge,
        )
    )
    
    
    import_price = entry.options.get("energy_import_price", entry.data.get("energy_import_price", 0.0))
    export_price = entry.options.get("energy_export_price", entry.data.get("energy_export_price", 0.0))
    
    import_price_val = float(import_price) if import_price > 0.0 else None
    export_price_val = float(export_price) if export_price > 0.0 else None

    # Add Grid Source
    energy_prefs["energy_sources"].append(
        {
            "type": "grid",
            "flow_from": [
                {
                    "stat_energy_from": grid_import,
                    "stat_cost": None,
                    "entity_energy_price": None,
                    "number_energy_price": import_price_val,
                }
            ],
            "flow_to": [
                {
                    "stat_energy_to": grid_export,
                    "stat_compensation": None,
                    "entity_energy_price": None,
                    "number_energy_price": export_price_val,
                }
            ],
            "cost_adjustment_day": 0.0,
        }
    )
    
    try:
        await manager.async_update(energy_prefs)
        msg = "Energy Dashboard was successfully configured automatically."
        _LOGGER.info(msg)
        persistent_notification.async_create(
            hass, msg, title="FoxESS Smart - Setup Complete"
        )
    except Exception as e:
        msg = f"Failed to update Energy Dashboard: {e}"
        _LOGGER.error(msg)
        persistent_notification.async_create(
            hass, msg, title="FoxESS Smart - Setup Failed"
        )
