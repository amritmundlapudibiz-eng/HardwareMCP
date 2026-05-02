"""
Unit Tests for HardwareMCP Simulator

This module contains comprehensive unit tests for the hardware simulator,
covering all 8 tools and their functionality:
1. read_temperature
2. read_voltage
3. read_current
4. read_can_message
5. read_gpio
6. read_imu
7. run_fault_detection
8. get_system_health
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from server.hal.simulator import (
    HardwareSimulator,
    get_simulator,
    TemperatureSensor,
    VoltageCell,
    CurrentChannel,
    GPIOPin,
    FaultType,
    SensorType
)


class TestTemperatureSensor:
    """Test TemperatureSensor class"""

    def test_temperature_sensor_creation(self):
        """Test creating a temperature sensor"""
        sensor = TemperatureSensor("test_sensor", 25.0, 2.0)
        assert sensor.name == "test_sensor"
        assert sensor.base_temp == 25.0
        assert sensor.variance == 2.0

    def test_temperature_reading_in_range(self):
        """Test that temperature readings are within expected range"""
        sensor = TemperatureSensor("test_sensor", 25.0, 2.0)
        for _ in range(100):
            temp = sensor.read()
            # Should be roughly within base_temp ± variance (with some drift)
            assert sensor.min_temp <= temp <= sensor.max_temp
            assert 20.0 <= temp <= 30.0  # Reasonable range

    def test_temperature_bounds(self):
        """Test that temperature respects min/max bounds"""
        sensor = TemperatureSensor(
            "test_sensor", 200.0, 100.0, min_temp=-40.0, max_temp=150.0)
        for _ in range(50):
            temp = sensor.read()
            assert -40.0 <= temp <= 150.0


class TestVoltageCell:
    """Test VoltageCell class"""

    def test_voltage_cell_creation(self):
        """Test creating a voltage cell"""
        cell = VoltageCell("cell_1", 3.7, 0.05)
        assert cell.name == "cell_1"
        assert cell.nominal_voltage == 3.7
        assert cell.variance == 0.05

    def test_voltage_reading_in_range(self):
        """Test that voltage readings are within expected range"""
        cell = VoltageCell("cell_1", 3.7, 0.05)
        for _ in range(100):
            voltage = cell.read()
            assert cell.min_voltage <= voltage <= cell.max_voltage
            assert 3.5 <= voltage <= 3.9  # Reasonable range


class TestCurrentChannel:
    """Test CurrentChannel class"""

    def test_current_channel_creation(self):
        """Test creating a current channel"""
        channel = CurrentChannel("motor", 45.0, 10.0)
        assert channel.name == "motor"
        assert channel.base_current == 45.0
        assert channel.variance == 10.0

    def test_current_reading_in_range(self):
        """Test that current readings are within expected range"""
        channel = CurrentChannel("motor", 45.0, 10.0)
        for _ in range(100):
            current = channel.read()
            assert channel.min_current <= current <= channel.max_current
            assert 0.0 <= current <= 100.0


class TestGPIOPin:
    """Test GPIOPin class"""

    def test_gpio_pin_creation(self):
        """Test creating a GPIO pin"""
        pin = GPIOPin(0, "input")
        assert pin.pin_number == 0
        assert pin.mode == "input"
        assert pin.state is False

    def test_gpio_input_read(self):
        """Test reading from an input pin"""
        pin = GPIOPin(0, "input")
        # Input pins can change state randomly
        states = [pin.read() for _ in range(100)]
        assert all(isinstance(s, bool) for s in states)

    def test_gpio_output_write(self):
        """Test writing to an output pin"""
        pin = GPIOPin(2, "output")
        pin.write(True)
        assert pin.state is True
        pin.write(False)
        assert pin.state is False

    def test_gpio_output_read(self):
        """Test reading from an output pin"""
        pin = GPIOPin(2, "output")
        pin.write(True)
        assert pin.read() is True


class TestHardwareSimulator:
    """Test HardwareSimulator class"""

    @pytest.fixture
    def simulator(self):
        """Create a fresh simulator instance for each test"""
        return HardwareSimulator()

    @pytest.mark.asyncio
    async def test_read_temperature_engine(self, simulator):
        """Test reading engine temperature"""
        result = await simulator.read_temperature("engine")

        assert "sensor" in result
        assert result["sensor"] == "engine"
        assert "temperature_celsius" in result
        assert "temperature_fahrenheit" in result
        assert "timestamp" in result
        assert "unit" in result

        # Check temperature is reasonable
        temp_c = result["temperature_celsius"]
        assert 70.0 <= temp_c <= 100.0  # Engine temp range

        # Check Fahrenheit conversion
        temp_f = result["temperature_fahrenheit"]
        assert abs(temp_f - (temp_c * 9/5 + 32)) < 0.1

    @pytest.mark.asyncio
    async def test_read_temperature_all_sensors(self, simulator):
        """Test reading all temperature sensors"""
        sensors = ["engine", "battery", "ambient", "motor"]

        for sensor_name in sensors:
            result = await simulator.read_temperature(sensor_name)
            assert result["sensor"] == sensor_name
            assert isinstance(result["temperature_celsius"], (int, float))

    @pytest.mark.asyncio
    async def test_read_temperature_invalid_sensor(self, simulator):
        """Test reading from invalid temperature sensor"""
        with pytest.raises(ValueError, match="Unknown temperature sensor"):
            await simulator.read_temperature("invalid_sensor")

    @pytest.mark.asyncio
    async def test_read_voltage_cell(self, simulator):
        """Test reading voltage from a cell"""
        result = await simulator.read_voltage("cell_1")

        assert "cell" in result
        assert result["cell"] == "cell_1"
        assert "voltage" in result
        assert "timestamp" in result
        assert "unit" in result

        # Check voltage is reasonable
        voltage = result["voltage"]
        assert 2.5 <= voltage <= 4.2  # Li-ion cell range

    @pytest.mark.asyncio
    async def test_read_voltage_all_cells(self, simulator):
        """Test reading all voltage cells"""
        cells = ["cell_1", "cell_2", "cell_3", "cell_4"]

        for cell_name in cells:
            result = await simulator.read_voltage(cell_name)
            assert result["cell"] == cell_name
            assert isinstance(result["voltage"], (int, float))

    @pytest.mark.asyncio
    async def test_read_voltage_invalid_cell(self, simulator):
        """Test reading from invalid voltage cell"""
        with pytest.raises(ValueError, match="Unknown voltage cell"):
            await simulator.read_voltage("cell_99")

    @pytest.mark.asyncio
    async def test_read_current_channel(self, simulator):
        """Test reading current from a channel"""
        result = await simulator.read_current("motor")

        assert "channel" in result
        assert result["channel"] == "motor"
        assert "current" in result
        assert "timestamp" in result
        assert "unit" in result

        # Check current is reasonable
        current = result["current"]
        assert 0.0 <= current <= 100.0

    @pytest.mark.asyncio
    async def test_read_current_all_channels(self, simulator):
        """Test reading all current channels"""
        channels = ["motor", "bms", "aux"]

        for channel_name in channels:
            result = await simulator.read_current(channel_name)
            assert result["channel"] == channel_name
            assert isinstance(result["current"], (int, float))

    @pytest.mark.asyncio
    async def test_read_current_invalid_channel(self, simulator):
        """Test reading from invalid current channel"""
        with pytest.raises(ValueError, match="Unknown current channel"):
            await simulator.read_current("invalid_channel")

    @pytest.mark.asyncio
    async def test_read_can_message(self, simulator):
        """Test reading CAN bus message"""
        result = await simulator.read_can_message()

        assert "source" in result
        assert result["source"] == "Cascadia CM200DZ"
        assert "message" in result
        assert "timestamp" in result

        message = result["message"]
        assert "can_id" in message
        assert "data" in message
        assert "timestamp" in message
        assert "length" in message

        # Check CAN ID is in expected range
        can_id = message["can_id"]
        assert can_id in ["0xc0", "0xc1", "0xc2", "0xc3"]

        # Check data length
        assert len(message["data"]) == 8

    @pytest.mark.asyncio
    async def test_read_can_message_multiple(self, simulator):
        """Test reading multiple CAN messages"""
        messages = []
        for _ in range(10):
            result = await simulator.read_can_message()
            messages.append(result)

        # Should get different messages
        assert len(messages) == 10
        # At least some variety in CAN IDs
        can_ids = [m["message"]["can_id"] for m in messages]
        assert len(set(can_ids)) >= 2

    @pytest.mark.asyncio
    async def test_read_gpio_input(self, simulator):
        """Test reading GPIO input pin"""
        result = await simulator.read_gpio(0)

        assert "pin" in result
        assert result["pin"] == 0
        assert "mode" in result
        assert result["mode"] == "input"
        assert "state" in result
        assert "value" in result
        assert "timestamp" in result

        # State should be boolean
        assert isinstance(result["state"], bool)
        # Value should match state
        assert result["value"] == (1 if result["state"] else 0)

    @pytest.mark.asyncio
    async def test_read_gpio_output(self, simulator):
        """Test reading GPIO output pin"""
        result = await simulator.read_gpio(2)

        assert result["pin"] == 2
        assert result["mode"] == "output"
        assert isinstance(result["state"], bool)

    @pytest.mark.asyncio
    async def test_read_gpio_all_pins(self, simulator):
        """Test reading all GPIO pins"""
        for pin_number in range(6):
            result = await simulator.read_gpio(pin_number)
            assert result["pin"] == pin_number
            assert result["mode"] in ["input", "output"]

    @pytest.mark.asyncio
    async def test_read_gpio_invalid_pin(self, simulator):
        """Test reading from invalid GPIO pin"""
        with pytest.raises(ValueError, match="Unknown GPIO pin"):
            await simulator.read_gpio(99)

    @pytest.mark.asyncio
    async def test_write_gpio_output(self, simulator):
        """Test writing to GPIO output pin"""
        result = await simulator.write_gpio(2, True)

        assert "pin" in result
        assert result["pin"] == 2
        assert "state" in result
        assert result["state"] is True
        assert "success" in result
        assert result["success"] is True

        # Verify the write
        read_result = await simulator.read_gpio(2)
        assert read_result["state"] is True

    @pytest.mark.asyncio
    async def test_write_gpio_input_fails(self, simulator):
        """Test that writing to input pin fails"""
        with pytest.raises(ValueError, match="not configured as output"):
            await simulator.write_gpio(0, True)

    @pytest.mark.asyncio
    async def test_read_imu(self, simulator):
        """Test reading IMU data"""
        result = await simulator.read_imu()

        assert "accelerometer" in result
        assert "gyroscope" in result
        assert "timestamp" in result

        # Check accelerometer data
        accel = result["accelerometer"]
        assert "x" in accel
        assert "y" in accel
        assert "z" in accel
        assert "unit" in accel
        assert accel["unit"] == "m/s²"

        # Z-axis should be close to gravity
        assert 9.0 <= accel["z"] <= 10.5

        # Check gyroscope data
        gyro = result["gyroscope"]
        assert "x" in gyro
        assert "y" in gyro
        assert "z" in gyro
        assert "unit" in gyro
        assert gyro["unit"] == "rad/s"

    @pytest.mark.asyncio
    async def test_run_fault_detection(self, simulator):
        """Test fault detection"""
        result = await simulator.run_fault_detection()

        assert "total_faults" in result
        assert "critical_faults" in result
        assert "warning_faults" in result
        assert "faults" in result
        assert "timestamp" in result

        # Check fault counts are non-negative
        assert result["total_faults"] >= 0
        assert result["critical_faults"] >= 0
        assert result["warning_faults"] >= 0

        # Total should equal critical + warning
        assert result["total_faults"] == result["critical_faults"] + \
            result["warning_faults"]

        # Check fault structure
        for fault in result["faults"]:
            assert "type" in fault
            assert "sensor" in fault
            assert "value" in fault
            assert "threshold" in fault
            assert "timestamp" in fault
            assert "severity" in fault
            assert fault["severity"] in ["warning", "critical"]

    @pytest.mark.asyncio
    async def test_get_system_health(self, simulator):
        """Test getting system health"""
        result = await simulator.get_system_health()

        assert "status" in result
        assert "uptime_seconds" in result
        assert "metrics" in result
        assert "temperatures" in result
        assert "voltages" in result
        assert "currents" in result
        assert "fault_summary" in result
        assert "timestamp" in result

        # Check status is valid
        assert result["status"] in ["healthy",
                                    "warning", "degraded", "critical"]

        # Check metrics
        metrics = result["metrics"]
        assert "average_temperature" in metrics
        assert "average_voltage" in metrics
        assert "total_current" in metrics

        # Check temperatures
        temps = result["temperatures"]
        assert len(temps) == 4  # engine, battery, ambient, motor

        # Check voltages
        voltages = result["voltages"]
        assert len(voltages) == 4  # cell_1 through cell_4

        # Check currents
        currents = result["currents"]
        assert len(currents) == 3  # motor, bms, aux

        # Check fault summary
        fault_summary = result["fault_summary"]
        assert "critical" in fault_summary
        assert "warning" in fault_summary

    @pytest.mark.asyncio
    async def test_fault_detection_temperature(self, simulator):
        """Test that temperature faults are detected"""
        # Force a high temperature reading by modifying the sensor
        simulator.temperature_sensors["engine"].base_temp = 105.0
        simulator.temperature_sensors["engine"].variance = 0.1

        # Read temperature to trigger fault detection
        await simulator.read_temperature("engine")

        # Run fault detection
        result = await simulator.run_fault_detection()

        # Should have at least one temperature fault
        temp_faults = [f for f in result["faults"]
                       if f["type"] == "overtemperature"]
        assert len(temp_faults) > 0

    @pytest.mark.asyncio
    async def test_fault_detection_voltage(self, simulator):
        """Test that voltage faults are detected"""
        # Force a high voltage reading
        simulator.voltage_cells["cell_1"].nominal_voltage = 4.35
        simulator.voltage_cells["cell_1"].variance = 0.01

        # Read voltage to trigger fault detection
        await simulator.read_voltage("cell_1")

        # Run fault detection
        result = await simulator.run_fault_detection()

        # Should have at least one voltage fault
        voltage_faults = [f for f in result["faults"]
                          if f["type"] == "overvoltage"]
        assert len(voltage_faults) > 0

    @pytest.mark.asyncio
    async def test_fault_detection_current(self, simulator):
        """Test that current faults are detected"""
        # Force a high current reading
        simulator.current_channels["motor"].base_current = 98.0
        simulator.current_channels["motor"].variance = 0.5

        # Read current to trigger fault detection
        await simulator.read_current("motor")

        # Run fault detection
        result = await simulator.run_fault_detection()

        # Should have at least one current fault
        current_faults = [f for f in result["faults"]
                          if f["type"] == "overcurrent"]
        assert len(current_faults) > 0


class TestSimulatorSingleton:
    """Test the global simulator singleton"""

    def test_get_simulator_returns_same_instance(self):
        """Test that get_simulator returns the same instance"""
        sim1 = get_simulator()
        sim2 = get_simulator()
        assert sim1 is sim2

    def test_simulator_has_all_sensors(self):
        """Test that simulator has all required sensors"""
        sim = get_simulator()

        # Check temperature sensors
        assert "engine" in sim.temperature_sensors
        assert "battery" in sim.temperature_sensors
        assert "ambient" in sim.temperature_sensors
        assert "motor" in sim.temperature_sensors

        # Check voltage cells
        assert "cell_1" in sim.voltage_cells
        assert "cell_2" in sim.voltage_cells
        assert "cell_3" in sim.voltage_cells
        assert "cell_4" in sim.voltage_cells

        # Check current channels
        assert "motor" in sim.current_channels
        assert "bms" in sim.current_channels
        assert "aux" in sim.current_channels

        # Check GPIO pins
        for pin in range(6):
            assert pin in sim.gpio_pins


if __name__ == "__main__":
    """Run tests with pytest"""
    pytest.main([__file__, "-v", "--tb=short"])

# Made with Bob
