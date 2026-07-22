import unittest
from unittest.mock import MagicMock, patch

import tests.hass_mock
from custom_components.foxess_smart.modbus_client import (
    decode_s16,
    decode_u32_be,
    decode_s32_be,
    decode_u32_le,
    FoxESSModbusClient,
)


class TestModbusDecoders(unittest.TestCase):
    def test_decode_s16(self):
        self.assertEqual(decode_s16(0), 0)
        self.assertEqual(decode_s16(10), 10)
        self.assertEqual(decode_s16(32767), 32767)
        self.assertEqual(decode_s16(32768), -32768)
        self.assertEqual(decode_s16(65535), -1)

    def test_decode_u32_be(self):
        self.assertEqual(decode_u32_be([0, 4962]), 4962)
        self.assertEqual(decode_u32_be([1, 0]), 65536)

    def test_decode_s32_be(self):
        self.assertEqual(decode_s32_be([0, 4962]), 4962)
        self.assertEqual(decode_s32_be([32768, 0]), -2147483648)
        self.assertEqual(decode_s32_be([65535, 65535]), -1)

    def test_decode_u32_le(self):
        # Word swapped: [low, high] -> high << 16 | low
        self.assertEqual(decode_u32_le([1640, 0]), 1640)
        self.assertEqual(decode_u32_le([0, 1]), 65536)


class TestFoxESSModbusClient(unittest.TestCase):
    @patch("custom_components.foxess_smart.modbus_client.ModbusTcpClient")
    def test_read_registers_success(self, mock_tcp_client_cls):
        mock_instance = MagicMock()
        mock_tcp_client_cls.return_value = mock_instance
        mock_instance.connected = False
        mock_result = MagicMock()
        mock_result.isError.return_value = False
        mock_result.registers = [100, 200]
        mock_instance.read_holding_registers.return_value = mock_result

        client = FoxESSModbusClient("192.168.1.100", 502, 247)
        regs = client.read_registers(30001, 2)

        self.assertEqual(regs, [100, 200])
        mock_instance.connect.assert_called_once()
        mock_instance.read_holding_registers.assert_called_once_with(
            address=30001, count=2, slave=247
        )
        mock_instance.close.assert_called_once()

    @patch("custom_components.foxess_smart.modbus_client.ModbusTcpClient")
    def test_read_registers_error(self, mock_tcp_client_cls):
        mock_instance = MagicMock()
        mock_tcp_client_cls.return_value = mock_instance
        mock_instance.connected = True
        mock_result = MagicMock()
        mock_result.isError.return_value = True
        mock_instance.read_holding_registers.return_value = mock_result

        client = FoxESSModbusClient("192.168.1.100", 502, 247)
        with self.assertRaises(Exception) as ctx:
            client.read_registers(30001, 2)

        self.assertIn("Modbus error reading address 30001", str(ctx.exception))
        mock_instance.close.assert_called_once()

    @patch("custom_components.foxess_smart.modbus_client.ModbusTcpClient")
    def test_write_work_mode_success(self, mock_tcp_client_cls):
        mock_instance = MagicMock()
        mock_tcp_client_cls.return_value = mock_instance
        mock_instance.connected = False
        mock_result = MagicMock()
        mock_result.isError.return_value = False
        mock_instance.write_register.return_value = mock_result

        client = FoxESSModbusClient("192.168.1.100", 502, 247)
        client.write_work_mode(1)

        mock_instance.connect.assert_called_once()
        mock_instance.write_register.assert_called_once_with(
            address=49203, value=1, slave=247
        )
        mock_instance.close.assert_called_once()

    @patch("custom_components.foxess_smart.modbus_client.ModbusTcpClient")
    def test_write_work_mode_error(self, mock_tcp_client_cls):
        mock_instance = MagicMock()
        mock_tcp_client_cls.return_value = mock_instance
        mock_instance.connected = True
        mock_result = MagicMock()
        mock_result.isError.return_value = True
        mock_instance.write_register.return_value = mock_result

        client = FoxESSModbusClient("192.168.1.100", 502, 247)
        with self.assertRaises(Exception) as ctx:
            client.write_work_mode(1)

        self.assertIn("Modbus error writing work mode 1", str(ctx.exception))
        mock_instance.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
