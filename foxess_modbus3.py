#!/usr/bin/env python3

from pymodbus.client import ModbusTcpClient

HOST = "192.168.178.194"
PORT = 502
SLAVE = 247
TIMEOUT = 3

REGISTERS = [

    ("=== PV ===", None, None, None, None),

    ("PV1 Voltage",       39070, "U16",  0.1,   "V"),
    ("PV1 Current",       39071, "U16",  0.01,  "A"),
    ("PV1 Power",         39279, "S32",  0.001, "kW"),

    ("PV2 Voltage",       39072, "U16",  0.1,   "V"),
    ("PV2 Current",       39073, "U16",  0.01,  "A"),
    ("PV2 Power",         39281, "S32",  0.001, "kW"),


    ("=== Battery ===", None, None, None, None),

    ("Battery SoC",       37612, "U16",  1,     "%"),
    ("Battery Voltage",   37609, "U16",  0.1,   "V"),
    ("Battery Current",   37610, "S16",  0.1,   "A"),
    ("Battery Temp",      37611, "S16",  0.1,   "°C"),
    ("Battery Power",     39237, "S32",  0.001, "kW"),


    ("=== Grid ===", None, None, None, None),

    ("Grid Voltage R",    39123, "U16",  0.1,   "V"),
    ("Grid Voltage S",    39124, "U16",  0.1,   "V"),
    ("Grid Voltage T",    39125, "U16",  0.1,   "V"),

    ("Grid Current R",    39126, "S32",  0.001, "A"),
    ("Grid Current S",    39128, "S32",  0.001, "A"),
    ("Grid Current T",    39130, "S32",  0.001, "A"),

    ("Grid Power R",      39248, "S32",  0.001, "kW"),
    ("Grid Power S",      39250, "S32",  0.001, "kW"),
    ("Grid Power T",      39252, "S32",  0.001, "kW"),

    ("Grid CT Power",     39168, "S32",  0.001, "kW"),


    ("=== Load ===", None, None, None, None),

    ("Load Power Total",  39225, "S32",  0.001, "kW"),
    ("Load Power R",      39219, "S32",  0.001, "kW"),
    ("Load Power S",      39221, "S32",  0.001, "kW"),
    ("Load Power T",      39223, "S32",  0.001, "kW"),


    ("=== Energy ===", None, None, None, None),

    ("PV Today",          39604, "U32",  0.1,   "kWh"),
    ("PV Total",          39602, "U32",  0.1,   "kWh"),


    ("=== Control ===", None, None, None, None),

    ("Work Mode",         49203, "U16",  1,     "")
]


def s16(v):
    return v - 65536 if v >= 32768 else v


def s32(v):
    return v - 4294967296 if v >= 2147483648 else v


client = ModbusTcpClient(
    HOST,
    port=PORT,
    timeout=TIMEOUT
)

print(f"Connecting to {HOST}:{PORT} ...")

if not client.connect():
    print("Connection failed.")
    quit()

print("Connected.\n")

print("-" * 120)
print(f"{'Name':30} {'Addr':>6} {'Registers':18} {'Raw':>12} {'Value':>15}")
print("-" * 120)

for item in REGISTERS:

    name, addr, typ, scale, unit = item

    if addr is None:
        print()
        print(name)
        continue

    try:

        count = 2 if typ.endswith("32") else 1

        rr = client.read_holding_registers(
            address=addr,
            count=count,
            device_id=SLAVE
        )

        if rr.isError():
            print(f"{name:30} {addr:6} ERROR")
            continue

        regs = rr.registers

        if typ == "U16":
            raw = regs[0]

        elif typ == "S16":
            raw = s16(regs[0])

        elif typ == "U32":
            raw = (regs[0] << 16) | regs[1]

        elif typ == "S32":
            raw = s32((regs[0] << 16) | regs[1])

        value = raw * scale

        print(
            f"{name:30} "
            f"{addr:6} "
            f"{str(regs):18} "
            f"{raw:12} "
            f"{value:12.3f} {unit}"
        )

    except Exception as ex:
        print(f"{name:30} {addr:6} FAILED ({ex})")

client.close()

print("\nFinished.")
