"""Number platform for FoxESS H12 Smart integration."""

import logging
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

NUMBER_TYPES = {
    "min_soc": {
        "register": 41009,
        "min": 10,
        "max": 100,
    },
    "max_soc": {
        "register": 41010,
        "min": 10,
        "max": 100,
    },
    "min_soc_on_grid": {
        "register": 41011,
        "min": 10,
        "max": 100,
    },
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up FoxESS H12 number entities based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        FoxESSNumber(coordinator, key, info)
        for key, info in NUMBER_TYPES.items()
    ]
    async_add_entities(entities)


class FoxESSNumber(CoordinatorEntity, NumberEntity):
    """Representation of a FoxESS H12 Number entity for Modbus registers."""

    def __init__(self, coordinator, key, info):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._key = key
        self._register = info["register"]
        self._attr_translation_key = key
        self._attr_unique_id = f"foxess_smart_{key}_{coordinator.entry_id}"
        self._attr_native_min_value = info["min"]
        self._attr_native_max_value = info["max"]
        self._attr_native_step = 1
        self._attr_mode = NumberMode.BOX
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name="FoxESS H12 Smart Inverter",
            manufacturer="andreaswatch",
            model="H12 Smart",
        )

    @property
    def native_value(self):
        """Return the current value."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        int_val = int(value)
        _LOGGER.debug("Setting %s to %s via modbus register %s", self._key, int_val, self._register)
        
        # Write to inverter via executor thread since pymodbus blocks
        await self.hass.async_add_executor_job(
            self.coordinator.client.write_register, self._register, int_val
        )
        
        # Optimistically update the state and request a refresh
        if self.coordinator.data is not None:
            self.coordinator.data[self._key] = int_val
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
