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
        "Solar Power Total",
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
        "House Consumption Power",
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
        "Solar Yield Today",
        "kWh",
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
    ),
    "pv_production_total": (
        "Solar Yield Total",
        "kWh",
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
    ),
    "grid_import_total": (
        "Grid Consumption Energy",
        "kWh",
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
    ),
    "grid_export_total": (
        "Grid Return Energy",
        "kWh",
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
    ),
    "battery_charge_total": (
        "Battery Energy In",
        "kWh",
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
    ),
    "battery_discharge_total": (
        "Battery Energy Out",
        "kWh",
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
    ),
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up FoxESS H12 sensor entities based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        FoxESSSensor(coordinator, key, info)
        for key, info in SENSOR_TYPES.items()
    ]
    
    async_add_entities(entities)


class FoxESSSensor(CoordinatorEntity, SensorEntity):
    """Representation of a FoxESS H12 sensor."""

    def __init__(self, coordinator, key, info):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        name_suffix, unit, device_class, state_class = info
        self._attr_name = name_suffix
        self._attr_unique_id = f"foxess_smart_{key}_{coordinator.entry_id}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_has_entity_name = True
        if device_class in (SensorDeviceClass.VOLTAGE, SensorDeviceClass.CURRENT, SensorDeviceClass.TEMPERATURE):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name="FoxESS H12 Smart Inverter",
            manufacturer="andreaswatch",
            model="H12 Smart",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)




