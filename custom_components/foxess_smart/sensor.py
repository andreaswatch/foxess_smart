"""Sensor platform for FoxESS H12 Smart integration."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfCurrent,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVoltage,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

SENSOR_TYPES = {
    "pv1_voltage": (
        "PV1 Voltage",
        UnitOfVoltage.VOLT,
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "pv1_current": (
        "PV1 Current",
        UnitOfCurrent.AMPERE,
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "pv1_power": (
        "PV1 Power",
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "pv2_voltage": (
        "PV2 Voltage",
        UnitOfVoltage.VOLT,
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "pv2_current": (
        "PV2 Current",
        UnitOfCurrent.AMPERE,
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "pv2_power": (
        "PV2 Power",
        UnitOfPower.KILO_WATT,
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
        UnitOfVoltage.VOLT,
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "battery_current": (
        "Battery BMS1 Current",
        UnitOfCurrent.AMPERE,
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "battery_temp": (
        "Battery BMS1 Temperature",
        UnitOfTemperature.CELSIUS,
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
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_voltage_r": (
        "Grid Voltage R",
        UnitOfVoltage.VOLT,
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_voltage_s": (
        "Grid Voltage S",
        UnitOfVoltage.VOLT,
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_voltage_t": (
        "Grid Voltage T",
        UnitOfVoltage.VOLT,
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_current_r": (
        "Grid Current R",
        UnitOfCurrent.AMPERE,
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_current_s": (
        "Grid Current S",
        UnitOfCurrent.AMPERE,
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_current_t": (
        "Grid Current T",
        UnitOfCurrent.AMPERE,
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_power_r": (
        "Grid Power R",
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_power_s": (
        "Grid Power S",
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_power_t": (
        "Grid Power T",
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_ct_power": (
        "Grid CT Power",
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "load_power_total": (
        "Load Power Total",
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "load_power_r": (
        "Load Power R",
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "load_power_s": (
        "Load Power S",
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "load_power_t": (
        "Load Power T",
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "pv_production_today": (
        "PV Production Today",
        UnitOfEnergy.KILO_WATT_HOUR,
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
    ),
    "pv_production_total": (
        "PV Production Total",
        UnitOfEnergy.KILO_WATT_HOUR,
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
    ),
    # Unidirectional metrics for Riemann Sum integration
    "grid_import_power": (
        "Grid Import Power",
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "grid_export_power": (
        "Grid Export Power",
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "battery_charge_power": (
        "Battery Charge Power",
        UnitOfPower.KILO_WATT,
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
    ),
    "battery_discharge_power": (
        "Battery Discharge Power",
        UnitOfPower.KILO_WATT,
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
