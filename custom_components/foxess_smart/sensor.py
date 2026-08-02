"""Sensor platform for FoxESS H12 Smart integration."""

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import callback
from homeassistant.util import dt as dt_util
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "pv1_voltage": (
        "PV1 Voltage",
        "V",
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "pv1_current": (
        "PV1 Current",
        "A",
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "pv1_power": (
        "PV1 Power",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "pv2_voltage": (
        "PV2 Voltage",
        "V",
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "pv2_current": (
        "PV2 Current",
        "A",
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "pv2_power": (
        "PV2 Power",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "pv_power_total": (
        "PV Power Total",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "battery_soc": (
        "Battery BMS1 SoC",
        PERCENTAGE,
        SensorDeviceClass.BATTERY,
        SensorStateClass.MEASUREMENT,
    ),
    "battery_voltage": (
        "Battery BMS1 Voltage",
        "V",
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "battery_current": (
        "Battery BMS1 Current",
        "A",
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "battery_temp": (
        "Battery BMS1 Temperature",
        "°C",
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
    ),
    "battery_bms2_soc": (
        "Battery BMS2 SoC",
        PERCENTAGE,
        SensorDeviceClass.BATTERY,
        SensorStateClass.MEASUREMENT,
    ),
    "battery_combined_power": (
        "Battery Charge/Discharge Power",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_voltage_r": (
        "Grid Voltage L1",
        "V",
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_voltage_s": (
        "Grid Voltage L2",
        "V",
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_voltage_t": (
        "Grid Voltage L3",
        "V",
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_current_r": (
        "Grid Current L1",
        "A",
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_current_s": (
        "Grid Current L2",
        "A",
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_current_t": (
        "Grid Current L3",
        "A",
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_power_r": (
        "Grid Power L1",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_power_s": (
        "Grid Power L2",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_power_t": (
        "Grid Power L3",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_ct_power": (
        "Grid Import/Export Power",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "load_power_total": (
        "Load Power Total",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "load_power_r": (
        "Load Power L1",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "load_power_s": (
        "Load Power L2",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "load_power_t": (
        "Load Power L3",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "pv_production_today": (
        "PV Production Today",
        "kWh",
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
    ),
    "pv_production_total": (
        "PV Production Total",
        "kWh",
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
    ),
    # Unidirectional metrics for Riemann Sum integration
    "grid_import_power": (
        "Grid Import Power",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_export_power": (
        "Grid Export Power",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "battery_charge_power": (
        "Battery Charge Power",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "battery_discharge_power": (
        "Battery Discharge Power",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up FoxESS H12 sensor entities based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        FoxESSSensor(coordinator, key, info)
        for key, info in SENSOR_TYPES.items()
    ]
    
    # Add virtual integral sensors for Energy Dashboard and general dashboard
    integral_sensors = [
        ("grid_import_power", "Grid Import Energy", SensorStateClass.TOTAL_INCREASING),
        ("grid_export_power", "Grid Export Energy", SensorStateClass.TOTAL_INCREASING),
        ("battery_charge_power", "Battery Charge Energy", SensorStateClass.TOTAL_INCREASING),
        ("battery_discharge_power", "Battery Discharge Energy", SensorStateClass.TOTAL_INCREASING),
        ("grid_ct_power", "Grid Import/Export Energy", SensorStateClass.TOTAL),
        ("battery_combined_power", "Battery Charge/Discharge Energy", SensorStateClass.TOTAL),
    ]
    for power_key, name_suffix, state_class in integral_sensors:
        entities.append(FoxESSEnergyIntegralSensor(coordinator, power_key, name_suffix, state_class))
        
    async_add_entities(entities)


class FoxESSSensor(CoordinatorEntity, SensorEntity):
    """Representation of a FoxESS H12 sensor."""

    def __init__(self, coordinator, key, info):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        name_suffix, unit, device_class, state_class = info
        self._attr_name = name_suffix
        self._attr_unique_id = f"foxess_smart_{key}_{coordinator.client.host}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_has_entity_name = True
        if device_class in (SensorDeviceClass.VOLTAGE, SensorDeviceClass.CURRENT, SensorDeviceClass.TEMPERATURE):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.client.host)},
            name="FoxESS H12 Smart Inverter",
            manufacturer="FoxESS",
            model="H12 Smart",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)




class FoxESSEnergyIntegralSensor(CoordinatorEntity, RestoreSensor):
    """Virtual sensor computing Energy (kWh) from Power (kW) via Riemann sum.

    Uses RestoreSensor to persist state across Home Assistant restarts,
    ensuring continuity for TOTAL_INCREASING energy statistics.
    """

    def __init__(self, coordinator, power_key, name_suffix, state_class=SensorStateClass.TOTAL_INCREASING):
        """Initialize the virtual integral sensor."""
        super().__init__(coordinator)
        self._power_key = power_key
        self._attr_name = name_suffix
        self._attr_unique_id = f"foxess_smart_{power_key}_integral_{coordinator.client.host}"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = state_class
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.client.host)},
            name="FoxESS H12 Smart Inverter",
            manufacturer="FoxESS",
            model="H12 Smart",
        )
        self._state = 0.0
        self._last_update_time = None
        self._last_power = None

    async def async_added_to_hass(self):
        """Restore state when entity is added to Home Assistant."""
        await super().async_added_to_hass()
        if state := await self.async_get_last_sensor_data():
            if state.native_value is not None:
                try:
                    self._state = float(state.native_value)
                except ValueError:
                    self._state = 0.0

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        power = self.coordinator.data.get(self._power_key)
        now = dt_util.utcnow()

        if power is not None:
            if self._last_update_time is not None and self._last_power is not None:
                # Delta time in hours
                delta_h = (now - self._last_update_time).total_seconds() / 3600.0
                # Trapezoidal Riemann sum integration (bounded 0 < delta_h < 1.0)
                if 0.0 < delta_h < 1.0:
                    self._state += 0.5 * (self._last_power + power) * delta_h

            self._last_power = power
            self._last_update_time = now

        super()._handle_coordinator_update()

    @property
    def native_value(self):
        """Return the integrated state rounded to 3 decimals."""
        return round(self._state, 3)


