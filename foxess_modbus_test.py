#!/usr/bin/env python3

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import time

HOST = "192.168.178.194"
PORT = 502
SLAVE = 247

# FoxESS Registerbereiche
#TEST_REGISTERS = [
#    30000,  # allgemeine Inverterdaten
#    31000,  # H3 Registerblock (wird von HA gelesen)
#    40000,  # Input/Control Bereich
#    41000,  # Write/Registerbereich (nur lesen!)
#]

#TEST_REGISTERS = [
#    30000,
#    30010,
#    30020,
#    30100,
#    31000,
#    32000,
#    33000,
#]

#TEST_REGISTERS = [
#    30000,
#    30050,
#    30060,
#    30070,
#    30080,
#    30090,
#]

#TEST_REGISTERS = [
#    31000,
#    30050,
#    30100
#]

#TEST_REGISTERS = [
#    30000,
#    30001,
#    30002,
#    30003,
#    30004,
#    30005,
#    30006,
#    30007,
#    30008,
#    30009,
#    30020,
#]


TEST_REGISTERS = [
    30040,
    30050,
    30060,
    30070,
    30080,
    30090,
]

client = ModbusTcpClient(
    HOST,
    port=PORT,
    timeout=5
)

print(f"Verbinde zu {HOST}:{PORT} ...")

if not client.connect():
    print("FEHLER: TCP Verbindung fehlgeschlagen")
    exit(1)

print("TCP Verbindung OK\n")

for reg in TEST_REGISTERS:
    try:
        print(f"Lese Register {reg} ...")

        result = client.read_holding_registers(
        #result = client.read_input_registers(
            address=reg,
            count=10,
            device_id=SLAVE
        )

        if result.isError():
            print("  Modbus Fehler:", result)

        else:
            print("  Antwort erhalten:")
            print(" ", result.registers)
            print(
                "".join(
                    chr(x >> 8) + chr(x & 0xff)
                    for x in result.registers
                    if x != 0
                )
            )

    except ModbusException as e:
        print("  Modbus Exception:", e)

    except Exception as e:
        print("  Fehler:", e)

    time.sleep(1)

client.close()

print("\nTest beendet")
