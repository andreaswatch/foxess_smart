#!/usr/bin/env python3

from pymodbus.client import ModbusTcpClient

HOST = "192.168.178.194"
PORT = 502
SLAVE = 247


def decode_ascii(registers):
    chars = []

    for r in registers:
        high = (r >> 8) & 0xff
        low = r & 0xff

        if high != 0:
            chars.append(chr(high))
        if low != 0:
            chars.append(chr(low))

    return "".join(chars)


client = ModbusTcpClient(
    HOST,
    port=PORT,
    timeout=3
)

print(f"Connecting to {HOST}:{PORT} ...")

if not client.connect():
    print("Connection failed")
    quit()

print("Connected\n")

start = 30000
count = 20

print(f"Reading registers {start}-{start+count-1} ...\n")

result = client.read_holding_registers(
    address=start,
    count=count,
    device_id=SLAVE
)

if result.isError():
    print("Modbus error:")
    print(result)
else:
    regs = result.registers

    print("Raw registers:")
    for i, value in enumerate(regs):
        print(f"{start+i}: {value}")

    print("\nASCII decode:")
    print(decode_ascii(regs))


client.close()
