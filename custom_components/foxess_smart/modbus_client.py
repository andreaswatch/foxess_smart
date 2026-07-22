"""Modbus TCP client wrapper and decoder functions for FoxESS H12 Smart."""

from pymodbus.client import ModbusTcpClient


def decode_s16(val: int) -> int:
    """Decode 16-bit signed integer (two's complement)."""
    return val - 65536 if val >= 32768 else val


def decode_u32_be(regs: list) -> int:
    """Decode 32-bit unsigned integer (Big-Endian word order)."""
    return (regs[0] << 16) | regs[1]


def decode_s32_be(regs: list) -> int:
    """Decode 32-bit signed integer (Big-Endian word order, two's complement)."""
    val = decode_u32_be(regs)
    return val - 4294967296 if val >= 2147483648 else val


def decode_u32_le(regs: list) -> int:
    """Decode 32-bit unsigned integer (Little-Endian word order, word swapped)."""
    return (regs[1] << 16) | regs[0]


class FoxESSModbusClient:
    """Wrapper around pymodbus ModbusTcpClient for FoxESS H12 Smart inverter."""

    def __init__(self, host: str, port: int, slave: int):
        """Initialize the Modbus TCP client wrapper."""
        self.host = host
        self.port = port
        self.slave = slave
        self.client = ModbusTcpClient(self.host, port=self.port, timeout=3)

    def read_registers(self, address: int, count: int) -> list:
        """Read registers and close immediately to prevent connection lock."""
        try:
            if not self.client.connected:
                self.client.connect()
            result = self.client.read_holding_registers(
                address=address, count=count, device_id=self.slave
            )
            if result.isError():
                raise Exception(f"Modbus error reading address {address}: {result}")
            return result.registers
        finally:
            self.client.close()

    def write_work_mode(self, value: int):
        """Write work mode value to holding register 49203."""
        try:
            if not self.client.connected:
                self.client.connect()
            result = self.client.write_register(
                address=49203, value=value, device_id=self.slave
            )
            if result.isError():
                raise Exception(f"Modbus error writing work mode {value}: {result}")
        finally:
            self.client.close()
