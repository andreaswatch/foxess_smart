#!/usr/bin/env python3

from pymodbus.client import ModbusTcpClient

HOST = "192.168.178.194"
PORT = 502
SLAVE = 247

REGISTER = 49203


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


# Vorher lesen
print(f"Reading Work Mode register {REGISTER} ...")

read = client.read_holding_registers(
    address=REGISTER,
    count=1,
    device_id=SLAVE
)

if read.isError():
    print("Read failed:")
    print(read)
    client.close()
    quit()

current = read.registers[0]

print(f"Current Work Mode: {current}")


# Nur gleichen Wert zurückschreiben
print()
print(f"Writing same value back: {current}")

write = client.write_register(
    address=REGISTER,
    value=current,
    device_id=SLAVE
)

if write.isError():
    print("Write failed:")
    print(write)
else:
    print("Write successful")


# Kontrolle
print()
print("Reading back...")

verify = client.read_holding_registers(
    address=REGISTER,
    count=1,
    device_id=SLAVE
)

if verify.isError():
    print("Verify failed:")
else:
    print(f"New Work Mode: {verify.registers[0]}")


client.close()

print("\nFinished.")
