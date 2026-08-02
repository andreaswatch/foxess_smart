"""Select platform for FoxESS H12 Smart integration."""

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.const import EntityCategory

from .const import DOMAIN, WORK_MODES, WORK_MODES_INV


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up FoxESS H12 select entity based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FoxESSWorkModeSelect(coordinator)])


class FoxESSWorkModeSelect(CoordinatorEntity, SelectEntity):
    """Representation of a FoxESS H12 Work Mode select entity."""

    def __init__(self, coordinator):
        """Initialize the work mode select entity."""
        super().__init__(coordinator)
        self._attr_name = "Work Mode"
        self._attr_unique_id = f"foxess_smart_work_mode_{coordinator.entry_id}"
        self._attr_options = list(WORK_MODES.keys())
        self._attr_has_entity_name = True
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name="FoxESS H12 Smart Inverter",
            manufacturer="andreaswatch",
            model="H12 Smart",
        )

    @property
    def current_option(self) -> str:
        """Return the selected entity option to represent the entity state."""
        if self.coordinator.data is None:
            return None
        val = self.coordinator.data.get("work_mode")
        if val is None:
            return None
        return WORK_MODES_INV.get(val, "Self Use")

    async def async_select_option(self, option: str) -> None:
        """Change the work mode of the inverter."""
        val = WORK_MODES.get(option)
        if val is not None:
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.client.write_work_mode, val
            )
            # Force immediately updating coordinator state
            await self.coordinator.async_request_refresh()


