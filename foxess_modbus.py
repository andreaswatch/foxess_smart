#!/usr/bin/env python3

from pymodbus.client import ModbusTcpClient

HOST = "192.168.178.195"
PORT = 502
SLAVE = 247

REGISTERS = [

    ("PV1 Voltage",39070,"U16",0.1,"V"),
    ("PV1 Current",39071,"U16",0.01,"A"),
    ("PV1 Power",39279,"S32R",0.001,"kW"),

    ("PV2 Voltage",39072,"U16",0.1,"V"),
    ("PV2 Current",39073,"U16",0.01,"A"),
    ("PV2 Power",39281,"S32R",0.001,"kW"),

    ("Battery SoC",37612,"U16",1,"%"),
    ("Battery Voltage",37609,"U16",0.1,"V"),
    ("Battery Current",37610,"S16",0.1,"A"),
    ("Battery Temp",37611,"S16",0.1,"°C"),
    ("Battery Power",39237,"S32R",0.001,"kW"),

    ("Grid Voltage R",39123,"U16",0.1,"V"),
    ("Grid Voltage S",39124,"U16",0.1,"V"),
    ("Grid Voltage T",39125,"U16",0.1,"V"),

    ("Grid Current R",39126,"S32R",0.001,"A"),
    ("Grid Current S",39128,"S32R",0.001,"A"),
    ("Grid Current T",39130,"S32R",0.001,"A"),

    ("Grid Power R",39248,"S32R",0.001,"kW"),
    ("Grid Power S",39250,"S32R",0.001,"kW"),
    ("Grid Power T",39252,"S32R",0.001,"kW"),

    ("Grid CT Power",39168,"S32R",0.001,"kW"),

    ("Load Power Total",39225,"S32R",0.001,"kW"),
    ("Load Power R",39219,"S32R",0.001,"kW"),
    ("Load Power S",39221,"S32R",0.001,"kW"),
    ("Load Power T",39223,"S32R",0.001,"kW"),

    ("PV Today",39604,"U32R",0.1,"kWh"),
    ("PV Total",39602,"U32R",0.1,"kWh"),

    ("Work Mode",49203,"U16",1,"")
]


def s16(v):
    if v >= 32768:
        v -= 65536
    return v


def s32(v):
    if v >= 2147483648:
        v -= 4294967296
    return v


client = ModbusTcpClient(HOST, port=PORT, timeout=3)

if not client.connect():
    print("Connection failed")
    quit()

print()
print("="*90)
print(f"{'Name':30} {'Addr':>6} {'Raw':>12} {'Value':>18}")
print("="*90)

for name, addr, typ, scale, unit in REGISTERS:

    try:

        count = 2 if "32" in typ else 1

        rr = client.read_holding_registers(
            address=addr,
            count=count,
            device_id=SLAVE
        )

        if rr.isError():
            print(f"{name:30} {addr:6} FAILED")
            continue

        if typ == "U16":
            raw = rr.registers[0]
            value = raw * scale

        elif typ == "S16":
            raw = s16(rr.registers[0])
            value = raw * scale

        elif typ == "U32R":
            raw = (rr.registers[1] << 16) | rr.registers[0]
            value = raw * scale

        elif typ == "S32R":
            raw = (rr.registers[1] << 16) | rr.registers[0]
            raw = s32(raw)
            value = raw * scale

        print(f"{name:30} {addr:6} {raw:12} {value:15.3f} {unit}")

    except Exception as e:
        print(f"{name:30} {addr:6} EXCEPTION {e}")

client.close()
