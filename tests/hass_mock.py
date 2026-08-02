import sys
from unittest.mock import MagicMock

# Define real classes for bases to avoid subclassing MagicMock instances
class DummyDataUpdateCoordinator:
    def __init__(self, hass, logger, *, name, update_interval, update_method=None):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.data = {}
    async def async_config_entry_first_refresh(self):
        pass
    async def async_request_refresh(self):
        pass

class DummyCoordinatorEntity:
    def __init__(self, coordinator, context=None):
        self.coordinator = coordinator
    def _handle_coordinator_update(self) -> None:
        pass
    def async_write_ha_state(self) -> None:
        pass


class DummySelectEntity:
    pass

class DummySensorEntity:
    pass

# Create mock modules
ha_mock = MagicMock()
core_mock = MagicMock()
core_mock.callback = lambda f: f

config_entries_mock = MagicMock()
const_mock = MagicMock()

helpers_mock = MagicMock()
update_coordinator_mock = MagicMock()
update_coordinator_mock.DataUpdateCoordinator = DummyDataUpdateCoordinator
update_coordinator_mock.CoordinatorEntity = DummyCoordinatorEntity
update_coordinator_mock.UpdateFailed = Exception
helpers_mock.update_coordinator = update_coordinator_mock

components_mock = MagicMock()
sensor_mock = MagicMock()
sensor_mock.SensorEntity = DummySensorEntity
sensor_mock.SensorDeviceClass = MagicMock()
sensor_mock.SensorStateClass = MagicMock()
components_mock.sensor = sensor_mock

select_mock = MagicMock()
select_mock.SelectEntity = DummySelectEntity
components_mock.select = select_mock

energy_mock = MagicMock()
energy_data_mock = MagicMock()
energy_mock.data = energy_data_mock
components_mock.energy = energy_mock

persistent_notification_mock = MagicMock()
components_mock.persistent_notification = persistent_notification_mock

sys.modules["homeassistant"] = ha_mock
sys.modules["homeassistant.core"] = core_mock
sys.modules["homeassistant.config_entries"] = config_entries_mock
sys.modules["homeassistant.const"] = const_mock
sys.modules["homeassistant.helpers"] = helpers_mock
sys.modules["homeassistant.helpers.update_coordinator"] = update_coordinator_mock
device_registry_mock = MagicMock()
device_registry_mock.DeviceInfo = dict
sys.modules["homeassistant.helpers.device_registry"] = device_registry_mock
sys.modules["homeassistant.components"] = components_mock
sys.modules["homeassistant.components.sensor"] = sensor_mock
sys.modules["homeassistant.components.select"] = select_mock
sys.modules["homeassistant.components.energy"] = energy_mock
sys.modules["homeassistant.components.energy.data"] = energy_data_mock
sys.modules["homeassistant.components.persistent_notification"] = persistent_notification_mock

from datetime import datetime, timezone
from unittest.mock import AsyncMock

util_mock = MagicMock()
util_dt_mock = MagicMock()
util_dt_mock.utcnow.side_effect = lambda: datetime.now(timezone.utc)
util_mock.dt = util_dt_mock
sys.modules["homeassistant.util"] = util_mock
sys.modules["homeassistant.util.dt"] = util_dt_mock

class DummyRestoreSensor:
    async def async_added_to_hass(self):
        pass
    async def async_get_last_sensor_data(self):
        return None

sensor_mock.RestoreSensor = DummyRestoreSensor


