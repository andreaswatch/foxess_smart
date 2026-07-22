#!/usr/bin/env python3

from pymodbus.client import ModbusTcpClient

HOST = "192.168.178.194"
PORT = 502
SLAVE = 247

TESTS = [
    ("PV1 Power",        39279),
    ("Battery Power",    39237),
    ("Grid Current R",   39126),
    ("Grid Current S",   39128),
    ("Grid Current T",   39130),
    ("Grid Power R",     39248),
    ("Grid Power S",     39250),
    ("Grid Power T",     39252),
    ("Grid CT Power",    39168),
    ("Load Power Total", 39225),
]


def s32(v):
    if v >= 0x80000000:
        v -= 0x100000000
    return v


client = ModbusTcpClient(HOST, port=PORT, timeout=3)

if not client.connect():
    print("Connection failed")
    quit()

print("=" * 100)

for name, addr in TESTS:

    rr = client.read_holding_registers(
        address=addr,
        count=2,
        device_id=SLAVE
    )

    if rr.isError():
        print(f"{name:20} {addr}: FAILED")
        continue

    r0 = rr.registers[0]
    r1 = rr.registers[1]

    # High word zuerst
    be = (r0 << 16) | r1

    # Low word zuerst
    le = (r1 << 16) | r0

    print()
    print(f"{name}")
    print(f"Address : {addr}")
    print(f"Registers: [{r0}, {r1}]")
    print(f"HEX      : [{r0:04X}, {r1:04X}]")
    print(f"BE U32   : {be}")
    print(f"BE S32   : {s32(be)}")
    print(f"LE U32   : {le}")
    print(f"LE S32   : {s32(le)}")
    print(f"BE kW    : {s32(be)/1000:.3f}")
    print(f"LE kW    : {s32(le)/1000:.3f}")

print()
print("=" * 100)

client.close()
