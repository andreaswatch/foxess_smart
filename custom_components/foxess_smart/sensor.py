"""Sensor platform for FoxESS H12 Smart integration."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import callback
from homeassistant.util import dt as dt_util
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
        "Battery Combined Power",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_voltage_r": (
        "Grid Voltage R",
        "V",
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_voltage_s": (
        "Grid Voltage S",
        "V",
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_voltage_t": (
        "Grid Voltage T",
        "V",
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_current_r": (
        "Grid Current R",
        "A",
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_current_s": (
        "Grid Current S",
        "A",
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_current_t": (
        "Grid Current T",
        "A",
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_power_r": (
        "Grid Power R",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_power_s": (
        "Grid Power S",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_power_t": (
        "Grid Power T",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_ct_power": (
        "Grid CT Power",
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
        "Load Power R",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "load_power_s": (
        "Load Power S",
        "kW",
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "load_power_t": (
        "Load Power T",
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
    
    # Add virtual integral sensors for Energy Dashboard
    integral_sensors = [
        ("grid_import_power", "Grid Import Energy"),
        ("grid_export_power", "Grid Export Energy"),
        ("battery_charge_power", "Battery Charge Energy"),
        ("battery_discharge_power", "Battery Discharge Energy"),
    ]
    for power_key, name_suffix in integral_sensors:
        entities.append(FoxESSEnergyIntegralSensor(coordinator, power_key, name_suffix))
        
    async_add_entities(entities)


class FoxESSSensor(CoordinatorEntity, SensorEntity):
    """Representation of a FoxESS H12 sensor."""

    def __init__(self, coordinator, key, info):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        name_suffix, unit, device_class, state_class = info
        self._attr_name = f"FoxESS H12 {name_suffix}"
        self._attr_unique_id = f"foxess_smart_{key}_{coordinator.client.host}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)

    @property
    def device_info(self):
        """Return device information about this FoxESS inverter."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.client.host)},
            "name": "FoxESS H12 Smart Inverter",
            "manufacturer": "FoxESS",
            "model": "H12 Smart",
        }


class FoxESSEnergyIntegralSensor(CoordinatorEntity, SensorEntity):
    """Virtual sensor computing Energy (kWh) from Power (kW) via Riemann sum.

    Intentionally does NOT use RestoreSensor - starts at 0.0 on every HA
    restart. HA's TOTAL_INCREASING state class handles resets correctly and
    continues accumulating statistics in its own database without needing the
    in-memory state to persist across restarts.
    """

    def __init__(self, coordinator, power_key, name_suffix):
        """Initialize the virtual integral sensor."""
        super().__init__(coordinator)
        self._power_key = power_key
        self._attr_name = f"FoxESS H12 {name_suffix}"
        self._attr_unique_id = f"foxess_smart_{power_key}_integral_{coordinator.client.host}"
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._state = 0.0
        self._last_update_time = None
        self._last_power = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        power = self.coordinator.data.get(self._power_key)
        now = dt_util.utcnow()

        if power is not None:
            if self._last_update_time is not None and self._last_power is not None:
                # Delta time in hours
                delta_h = (now - self._last_update_time).total_seconds() / 3600.0
                # Trapezoidal Riemann sum integration
                self._state += 0.5 * (self._last_power + power) * delta_h

            self._last_power = power
            self._last_update_time = now

        super()._handle_coordinator_update()

    @property
    def native_value(self):
        """Return the integrated state rounded to 3 decimals."""
        return round(self._state, 3)

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.client.host)},
            "name": "FoxESS H12 Smart Inverter",
            "manufacturer": "FoxESS",
            "model": "H12 Smart",
        }
