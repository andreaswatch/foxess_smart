# FoxESS H12 Smart Integration for Home Assistant
## Disclaimer

# Note 
This project was completely created by AI based on a provided register mapping file. It is merely a personal project that I had created for my own use.

The original Modbus register mapping source can be found here: [FoxESS ESPHome Modbus Direct Register Reading](https://marklabs.pl/en/foxess-esphome-modbus-direct-register-reading/)

**No liability or warranty is provided.** Use this integration entirely at your own risk. The author assumes no responsibility for any damages, malfunctions, or issues that may arise from using this software.


## About

This custom component integration allows local monitoring and control of the **FoxESS H12 Smart** inverter via **Modbus TCP** in Home Assistant.

## Features

- **Easy Setup**: Fully configurable through the Home Assistant UI (Config Flow).
- **Rich Sensor Data**:
  - **Battery**: Voltage, current, temperature, state of charge (SoC & BMS2 SoC), and power (combined, charge, and discharge).
  - **Photovoltaik (PV)**: Voltage, current, and power for PV String 1 & 2, total PV power, along with total and daily energy production.
  - **Grid**: Voltage and current per phase (R/S/T), CT power (import/export), and grid power per phase.
  - **Load**: Power consumption per phase (R/S/T) and total load power.
  - **Work Mode**: Current operational work mode.
- **Inverter Work Mode Control (Select Entity)**:
  - Supports switching between:
    - *Self Use*
    - *Feed-in First*
    - *Backup*
    - *Force Charge*
    - *Force Discharge*

## Installation

1. Copy the `custom_components/foxess_smart` directory into your Home Assistant's `custom_components` directory.
2. Restart Home Assistant.
3. Navigate to **Settings -> Devices & Services -> Add Integration** and search for **FoxESS H12 Smart**.
4. Enter the Inverter IP address (Host), port (default: 502), Modbus slave ID, and the scan interval.

## Energy Dashboard Configuration

To set up the official Home Assistant **Energy Dashboard** (**Settings -> Dashboards -> Energy**), map the following entities provided by this integration:

| Energy Dashboard Category | Entity | Description |
| :--- | :--- | :--- |
| **Solar Production** | `sensor.foxess_h12_pv_production_total` | Total solar production (kWh) |
| **Grid Consumption (Import)** | `sensor.foxess_h12_grid_import_energy` | Grid import energy (kWh, integral sensor) |
| **Return to Grid (Export)** | `sensor.foxess_h12_grid_export_energy` | Grid export energy (kWh, integral sensor) |
| **Battery Charge** | `sensor.foxess_h12_battery_charge_energy` | Energy stored into battery (kWh, integral sensor) |
| **Battery Discharge** | `sensor.foxess_h12_battery_discharge_energy` | Energy retrieved from battery (kWh, integral sensor) |

> **Note**: The grid import/export and battery charge/discharge energy sensors are automatically computed virtual integral sensors (Riemann sum), so no manual Home Assistant helpers are required.

## Power Flow Card Configuration

If using custom cards like [power-flow-card](https://github.com/LordGuenni/power-flow-card), configure the card using the following entities:

```yaml
type: custom:power-flow-card
entities:
  grid_power: sensor.foxess_h12_grid_ct_power
  solar_power: sensor.foxess_h12_pv_power_total
  battery_power: sensor.foxess_h12_battery_combined_power
  battery_soc: sensor.foxess_h12_battery_bms1_soc
  load_power: sensor.foxess_h12_load_power_total
```

## Testing and Development

The integration is covered by automated unit tests that mock the Home Assistant environment to verify client parsing, decoding, update coordinator logic, and entity properties.

To run the test suite locally:
```bash
PYTHONPATH=. python3 -m unittest discover -s tests
```

## Documentation and Modbus Mappings
Refer to the `docs/` folder for reference register mappings of the FoxESS H12 Modbus registers.

