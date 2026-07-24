#!/usr/bin/env python3
"""Diagnostic script to read raw Modbus registers from FoxESS H12 Smart inverter.

Usage:
    python3 scripts/test_inverter_live.py <inverter_ip> [port] [slave_id]
Example:
    python3 scripts/test_inverter_live.py 192.168.1.100 502 247
"""

import sys
import os

from pymodbus.client import ModbusTcpClient

def decode_s16(val: int) -> int:
    return val - 65536 if val >= 32768 else val

def decode_u32_be(regs: list) -> int:
    return (regs[0] << 16) | regs[1]

def decode_s32_be(regs: list) -> int:
    val = decode_u32_be(regs)
    return val - 4294967296 if val >= 2147483648 else val

def decode_u32_le(regs: list) -> int:
    return (regs[1] << 16) | regs[0]

def decode_s32_le(regs: list) -> int:
    val = decode_u32_le(regs)
    return val - 4294967296 if val >= 2147483648 else val

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/test_inverter_live.py <inverter_ip> [port] [slave_id]")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 502
    slave = int(sys.argv[3]) if len(sys.argv) > 3 else 247

    print(f"--- Connecting to FoxESS Inverter at {host}:{port} (Slave ID: {slave}) ---")
    client = ModbusTcpClient(host, port=port, timeout=5)

    if not client.connect():
        print(f"ERROR: Could not connect to {host}:{port}")
        sys.exit(1)

    def read_regs(address, count):
        try:
            res = client.read_holding_registers(address=address, count=count, slave=slave)
        except TypeError:
            res = client.read_holding_registers(address=address, count=count, device_id=slave)
        if res.isError():
            print(f"Error reading address {address}: {res}")
            return None
        return res.registers

    try:
        # PV Voltages / Currents (39070 - 39073)
        pv_vi = read_regs(39070, 4)
        print("\n=== PV Voltages & Currents (39070-39073) ===")
        if pv_vi:
            print(f"Raw registers: {pv_vi}")
            print(f"  PV1 Voltage: {pv_vi[0] * 0.1:.1f} V")
            print(f"  PV1 Current: {pv_vi[1] * 0.01:.2f} A")
            print(f"  PV2 Voltage: {pv_vi[2] * 0.1:.1f} V")
            print(f"  PV2 Current: {pv_vi[3] * 0.01:.2f} A")
            calc_pv1 = (pv_vi[0] * 0.1) * (pv_vi[1] * 0.01) / 1000.0
            calc_pv2 = (pv_vi[2] * 0.1) * (pv_vi[3] * 0.01) / 1000.0
            print(f"  --> Calculated PV1 Power (V*I): {calc_pv1:.3f} kW ({calc_pv1*1000:.1f} W)")
            print(f"  --> Calculated PV2 Power (V*I): {calc_pv2:.3f} kW ({calc_pv2*1000:.1f} W)")
            print(f"  --> Calculated Total PV Power: {calc_pv1+calc_pv2:.3f} kW ({(calc_pv1+calc_pv2)*1000:.1f} W)")

        # PV Power (39279 - 39282)
        pv_p = read_regs(39279, 4)
        print("\n=== PV Power Registers (39279-39282) ===")
        if pv_p:
            print(f"Raw registers: {pv_p}")
            pv1_be = decode_s32_be(pv_p[0:2])
            pv1_le = decode_s32_le(pv_p[0:2])
            pv2_be = decode_s32_be(pv_p[2:4])
            pv2_le = decode_s32_le(pv_p[2:4])
            print(f"  PV1 Raw BE (decode_s32_be): {pv1_be}  ->  * 0.001 = {pv1_be * 0.001:.3f} kW  |  * 0.0001 = {pv1_be * 0.0001:.3f} kW")
            print(f"  PV1 Raw LE (decode_s32_le): {pv1_le}  ->  * 0.001 = {pv1_le * 0.001:.3f} kW  |  * 0.0001 = {pv1_le * 0.0001:.3f} kW")
            print(f"  PV2 Raw BE (decode_s32_be): {pv2_be}  ->  * 0.001 = {pv2_be * 0.001:.3f} kW  |  * 0.0001 = {pv2_be * 0.0001:.3f} kW")
            print(f"  PV2 Raw LE (decode_s32_le): {pv2_le}  ->  * 0.001 = {pv2_le * 0.001:.3f} kW  |  * 0.0001 = {pv2_le * 0.0001:.3f} kW")

        # Grid CT Power (39168 - 39169)
        grid_ct = read_regs(39168, 2)
        print("\n=== Grid CT Power (39168-39169) ===")
        if grid_ct:
            print(f"Raw registers: {grid_ct}")
            ct_be = decode_s32_be(grid_ct)
            ct_le = decode_s32_le(grid_ct)
            print(f"  Grid CT BE: {ct_be} W -> {ct_be * 0.001:.3f} kW")
            print(f"  Grid CT LE: {ct_le} W -> {ct_le * 0.001:.3f} kW")

        # Load Power (39219 - 39226)
        load_p = read_regs(39219, 8)
        print("\n=== Load Power (39219-39226) ===")
        if load_p:
            print(f"Raw registers: {load_p}")
            load_tot_be = decode_s32_be(load_p[6:8])
            load_tot_le = decode_s32_le(load_p[6:8])
            print(f"  Load Total BE: {load_tot_be} W -> {load_tot_be * 0.001:.3f} kW")
            print(f"  Load Total LE: {load_tot_le} W -> {load_tot_le * 0.001:.3f} kW")

        # Battery Combined Power (39237 - 39238)
        bat_p = read_regs(39237, 2)
        print("\n=== Battery Combined Power (39237-39238) ===")
        if bat_p:
            print(f"Raw registers: {bat_p}")
            bat_be = decode_s32_be(bat_p)
            bat_le = decode_s32_le(bat_p)
            print(f"  Battery Power BE: {bat_be} W -> {bat_be * 0.001:.3f} kW")
            print(f"  Battery Power LE: {bat_le} W -> {bat_le * 0.001:.3f} kW")

        # PV Energy (39602 - 39605)
        pv_e = read_regs(39602, 4)
        print("\n=== PV Production Energy (39602-39605) ===")
        if pv_e:
            print(f"Raw registers: {pv_e}")
            tot_be = decode_u32_be(pv_e[0:2])
            tot_le = decode_u32_le(pv_e[0:2])
            today_be = decode_u32_be(pv_e[2:4])
            today_le = decode_u32_le(pv_e[2:4])
            print(f"  PV Production Total BE: {tot_be} -> * 0.1 = {tot_be * 0.1:.1f} kWh | * 1.0 = {tot_be:.1f} kWh")
            print(f"  PV Production Total LE: {tot_le} -> * 0.1 = {tot_le * 0.1:.1f} kWh | * 1.0 = {tot_le:.1f} kWh")
            print(f"  PV Production Today BE: {today_be} -> * 0.1 = {today_be * 0.1:.1f} kWh | * 1.0 = {today_be:.1f} kWh")
            print(f"  PV Production Today LE: {today_le} -> * 0.1 = {today_le * 0.1:.1f} kWh | * 1.0 = {today_le:.1f} kWh")

    finally:
        client.close()

if __name__ == '__main__':
    main()
