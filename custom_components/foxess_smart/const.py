"""Constants for FoxESS H12 Smart integration."""

DOMAIN = "foxess_smart"

# Work modes mapping (friendly name -> modbus register value)
WORK_MODES = {
    "Self Use": 1,
    "Feed-in First": 2,
    "Backup": 3,
    "Peak Shaving": 4,
    "Force Charge": 6,
    "Force Discharge": 7,
}

# Inverse mapping for reading
WORK_MODES_INV = {v: k for k, v in WORK_MODES.items()}
