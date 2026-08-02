# FoxESS Smart Home Assistant Integration

![FoxESS Smart Icon](custom_components/foxess_smart/icon.png)

A Home Assistant integration for **FoxESS H12 Smart** inverters (and potentially compatible H3 series) via Modbus TCP.

> **Note:** This integration was "vibe coded" (developed largely with AI assistance) and has **only been tested with a FoxESS H12 Smart** inverter. It focuses on a minimal, specific feature set tailored to this hardware, rather than attempting to support every FoxESS device on the market. Use at your own risk.

## Features

- **Local Polling:** Communicates directly with your FoxESS inverter over your local network using Modbus TCP.
- **Energy Dashboard Setup:** Includes an option to automatically configure the Home Assistant Energy Dashboard with the relevant Grid, Solar, and Battery sources.
- **Modbus Control:** Allows reading and writing of specific inverter settings directly from the Home Assistant UI:
  - Work Mode (Self Use, Back Up, Feed-in First, Force Time Use)
  - Min SoC (Netzbetrieb / On Grid)
  - Min SoC (Notstrom / Off Grid)
  - Max SoC
- **Options Flow:** Change IP addresses, ports, or timeouts via the UI without reinstalling the integration.
- **JSON Dump Service:** The `foxess_smart.get_all_values` service provides a JSON payload containing all currently tracked Modbus values.

## Installation

### Method 1: HACS
1. Open Home Assistant and go to **HACS**.
2. Click on the 3 dots in the top right corner and select **Custom repositories**.
3. Add the URL to this GitHub repository and select the category `Integration`.
4. Click **Install** on the `FoxESS Smart` integration.
5. Restart Home Assistant.

### Method 2: Manual Installation
1. Download the latest code from this repository.
2. Extract the `custom_components/foxess_smart` folder.
3. Copy the `foxess_smart` folder into your Home Assistant's `config/custom_components` directory.
4. Restart Home Assistant.

## Configuration

1. Go to **Settings > Devices & Services** in Home Assistant.
2. Click **Add Integration** and search for "FoxESS Smart".
3. Enter your inverter's IP Address (Host), Port (usually 502), and Slave ID (usually 3).
4. *(Optional)* Check the box to automatically configure your Energy Dashboard.

## Supported Hardware
- **FoxESS H12 Smart** (H3-12.0-E) - *Fully tested*
- Other FoxESS H3 series inverters with Modbus TCP *might* work, but are completely untested.

## License
This project is provided "as is". Feel free to fork, adapt, and use it in your own setup.
