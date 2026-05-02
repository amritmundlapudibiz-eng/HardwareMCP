"""
Hardware Abstraction Layer (HAL) Simulator

This module provides a realistic hardware simulator for testing and development
of the HardwareMCP server. It simulates various hardware components including:
- Temperature sensors (engine, battery, ambient, motor)
- Voltage cells (4 battery cells)
- Current channels (motor, BMS, auxiliary)
- CAN bus messages (Cascadia CM200DZ inverter)
- GPIO pins (digital I/O)
- IMU (accelerometer and gyroscope)
- Fault detection system
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import math


class SensorType(Enum):
    """Enumeration of sensor types"""
    TEMPERATURE = "temperature"
    VOLTAGE = "voltage"
    CURRENT = "current"
    CAN = "can"
    GPIO = "gpio"
    IMU = "imu"


class FaultType(Enum):
    """Enumeration of fault types"""
    OVERVOLTAGE = "overvoltage"
    UNDERVOLTAGE = "undervoltage"
    OVERTEMPERATURE = "overtemperature"
    OVERCURRENT = "overcurrent"


@dataclass
class Fault:
    """Represents a detected fault"""
    fault_type: FaultType
    sensor_name: str
    value: float
    threshold: float
    timestamp: datetime
    severity: str  # "warning", "critical"

    def to_dict(self) -> Dict[str, Any]:
        """Convert fault to dictionary"""
        return {
            "type": self.fault_type.value,
            "sensor": self.sensor_name,
            "value": self.value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity
        }


@dataclass
class TemperatureSensor:
    """Temperature sensor simulation"""
    name: str
    base_temp: float
    variance: float
    min_temp: float = -40.0
    max_temp: float = 150.0

    def read(self) -> float:
        """Read temperature with realistic variation"""
        temp = self.base_temp + random.uniform(-self.variance, self.variance)
        # Add slight drift over time
        drift = math.sin(time.time() / 100) * self.variance * 0.5
        temp += drift
        return max(self.min_temp, min(self.max_temp, temp))


@dataclass
class VoltageCell:
    """Battery cell voltage simulation"""
    name: str
    nominal_voltage: float
    variance: float
    min_voltage: float = 2.5
    max_voltage: float = 4.2

    def read(self) -> float:
        """Read cell voltage with realistic variation"""
        voltage = self.nominal_voltage + \
            random.uniform(-self.variance, self.variance)
        # Simulate slight discharge over time
        discharge = (time.time() % 3600) / 36000  # 0.1V drop per hour
        voltage -= discharge
        return max(self.min_voltage, min(self.max_voltage, voltage))


@dataclass
class CurrentChannel:
    """Current sensor simulation"""
    name: str
    base_current: float
    variance: float
    min_current: float = 0.0
    max_current: float = 100.0

    def read(self) -> float:
        """Read current with realistic variation"""
        current = self.base_current + \
            random.uniform(-self.variance, self.variance)
        # Add load variation
        load_factor = 1.0 + math.sin(time.time() / 10) * 0.2
        current *= load_factor
        return max(self.min_current, min(self.max_current, current))


@dataclass
class CANMessage:
    """CAN bus message"""
    can_id: int
    data: List[int]
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert CAN message to dictionary"""
        return {
            "can_id": hex(self.can_id),
            "data": [hex(b) for b in self.data],
            "timestamp": self.timestamp,
            "length": len(self.data)
        }


@dataclass
class GPIOPin:
    """GPIO pin simulation"""
    pin_number: int
    mode: str  # "input" or "output"
    state: bool = False

    def read(self) -> bool:
        """Read GPIO pin state"""
        if self.mode == "input":
            # Simulate random input changes occasionally
            if random.random() < 0.1:
                self.state = not self.state
        return self.state

    def write(self, state: bool) -> None:
        """Write GPIO pin state"""
        if self.mode == "output":
            self.state = state


@dataclass
class IMUData:
    """IMU (Inertial Measurement Unit) data"""
    accelerometer: Dict[str, Any]
    gyroscope: Dict[str, Any]
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert IMU data to dictionary"""
        return {
            "accelerometer": self.accelerometer,
            "gyroscope": self.gyroscope,
            "timestamp": self.timestamp
        }


class HardwareSimulator:
    """
    Main hardware simulator class that manages all simulated hardware components
    """

    # Fault thresholds
    TEMP_WARNING_THRESHOLD = 80.0
    TEMP_CRITICAL_THRESHOLD = 100.0
    VOLTAGE_MIN_WARNING = 3.0
    VOLTAGE_MIN_CRITICAL = 2.8
    VOLTAGE_MAX_WARNING = 4.1
    VOLTAGE_MAX_CRITICAL = 4.3
    CURRENT_WARNING_THRESHOLD = 80.0
    CURRENT_CRITICAL_THRESHOLD = 95.0

    def __init__(self):
        """Initialize the hardware simulator"""
        self._initialize_temperature_sensors()
        self._initialize_voltage_cells()
        self._initialize_current_channels()
        self._initialize_gpio_pins()
        self._faults: List[Fault] = []
        self._start_time = time.time()

    def _initialize_temperature_sensors(self) -> None:
        """Initialize temperature sensors"""
        self.temperature_sensors = {
            "engine": TemperatureSensor("engine", 85.0, 5.0),
            "battery": TemperatureSensor("battery", 35.0, 3.0),
            "ambient": TemperatureSensor("ambient", 25.0, 2.0),
            "motor": TemperatureSensor("motor", 65.0, 8.0)
        }

    def _initialize_voltage_cells(self) -> None:
        """Initialize battery voltage cells"""
        self.voltage_cells = {
            "cell_1": VoltageCell("cell_1", 3.7, 0.05),
            "cell_2": VoltageCell("cell_2", 3.72, 0.05),
            "cell_3": VoltageCell("cell_3", 3.68, 0.05),
            "cell_4": VoltageCell("cell_4", 3.71, 0.05)
        }

    def _initialize_current_channels(self) -> None:
        """Initialize current channels"""
        self.current_channels = {
            "motor": CurrentChannel("motor", 45.0, 10.0),
            "bms": CurrentChannel("bms", 2.5, 0.5, max_current=10.0),
            "aux": CurrentChannel("aux", 5.0, 1.0, max_current=20.0)
        }

    def _initialize_gpio_pins(self) -> None:
        """Initialize GPIO pins"""
        self.gpio_pins = {
            0: GPIOPin(0, "input"),
            1: GPIOPin(1, "input"),
            2: GPIOPin(2, "output"),
            3: GPIOPin(3, "output"),
            4: GPIOPin(4, "input"),
            5: GPIOPin(5, "output")
        }

    async def read_temperature(self, sensor_name: str) -> Dict[str, Any]:
        """
        Read temperature from a specific sensor

        Args:
            sensor_name: Name of the temperature sensor

        Returns:
            Dictionary containing temperature reading and metadata

        Raises:
            ValueError: If sensor name is invalid
        """
        if sensor_name not in self.temperature_sensors:
            raise ValueError(f"Unknown temperature sensor: {sensor_name}")

        sensor = self.temperature_sensors[sensor_name]
        temperature = sensor.read()

        # Check for faults
        self._check_temperature_fault(sensor_name, temperature)

        return {
            "sensor": sensor_name,
            "temperature_celsius": round(temperature, 2),
            "temperature_fahrenheit": round(temperature * 9/5 + 32, 2),
            "timestamp": datetime.now().isoformat(),
            "unit": "celsius"
        }

    async def read_voltage(self, cell_name: str) -> Dict[str, Any]:
        """
        Read voltage from a specific battery cell

        Args:
            cell_name: Name of the voltage cell

        Returns:
            Dictionary containing voltage reading and metadata

        Raises:
            ValueError: If cell name is invalid
        """
        if cell_name not in self.voltage_cells:
            raise ValueError(f"Unknown voltage cell: {cell_name}")

        cell = self.voltage_cells[cell_name]
        voltage = cell.read()

        # Check for faults
        self._check_voltage_fault(cell_name, voltage)

        return {
            "cell": cell_name,
            "voltage": round(voltage, 3),
            "timestamp": datetime.now().isoformat(),
            "unit": "volts"
        }

    async def read_current(self, channel_name: str) -> Dict[str, Any]:
        """
        Read current from a specific channel

        Args:
            channel_name: Name of the current channel

        Returns:
            Dictionary containing current reading and metadata

        Raises:
            ValueError: If channel name is invalid
        """
        if channel_name not in self.current_channels:
            raise ValueError(f"Unknown current channel: {channel_name}")

        channel = self.current_channels[channel_name]
        current = channel.read()

        # Check for faults
        self._check_current_fault(channel_name, current)

        return {
            "channel": channel_name,
            "current": round(current, 2),
            "timestamp": datetime.now().isoformat(),
            "unit": "amperes"
        }

    async def read_can_message(self) -> Dict[str, Any]:
        """
        Read a simulated CAN bus message from Cascadia CM200DZ inverter

        Returns:
            Dictionary containing CAN message data
        """
        # Simulate Cascadia CM200DZ inverter messages
        # Common CAN IDs for motor controllers: 0x0C0-0x0CF
        can_id = random.choice([0x0C0, 0x0C1, 0x0C2, 0x0C3])

        # Generate realistic data based on CAN ID
        if can_id == 0x0C0:  # Motor status
            data = [
                random.randint(0, 255),  # Status byte
                random.randint(0, 100),  # Speed LSB
                random.randint(0, 50),   # Speed MSB
                random.randint(0, 200),  # Torque
                random.randint(20, 80),  # Temperature
                0x00, 0x00, 0x00
            ]
        elif can_id == 0x0C1:  # Motor voltage/current
            data = [
                random.randint(100, 150),  # Voltage LSB
                random.randint(0, 5),      # Voltage MSB
                random.randint(0, 100),    # Current LSB
                random.randint(0, 50),     # Current MSB
                0x00, 0x00, 0x00, 0x00
            ]
        elif can_id == 0x0C2:  # Motor errors
            data = [
                0x00,  # No errors
                random.randint(0, 10),  # Warning count
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00
            ]
        else:  # 0x0C3 - Motor configuration
            data = [
                0x01,  # Mode
                random.randint(0, 255),
                random.randint(0, 255),
                0x00, 0x00, 0x00, 0x00, 0x00
            ]

        message = CANMessage(can_id, data, time.time())

        return {
            "source": "Cascadia CM200DZ",
            "message": message.to_dict(),
            "timestamp": datetime.now().isoformat()
        }

    async def read_gpio(self, pin_number: int) -> Dict[str, Any]:
        """
        Read GPIO pin state

        Args:
            pin_number: GPIO pin number

        Returns:
            Dictionary containing GPIO pin state and metadata

        Raises:
            ValueError: If pin number is invalid
        """
        if pin_number not in self.gpio_pins:
            raise ValueError(f"Unknown GPIO pin: {pin_number}")

        pin = self.gpio_pins[pin_number]
        state = pin.read()

        return {
            "pin": pin_number,
            "mode": pin.mode,
            "state": state,
            "value": 1 if state else 0,
            "timestamp": datetime.now().isoformat()
        }

    async def write_gpio(self, pin_number: int, state: bool) -> Dict[str, Any]:
        """
        Write GPIO pin state

        Args:
            pin_number: GPIO pin number
            state: Desired pin state

        Returns:
            Dictionary containing operation result

        Raises:
            ValueError: If pin number is invalid or pin is not an output
        """
        if pin_number not in self.gpio_pins:
            raise ValueError(f"Unknown GPIO pin: {pin_number}")

        pin = self.gpio_pins[pin_number]
        if pin.mode != "output":
            raise ValueError(f"Pin {pin_number} is not configured as output")

        pin.write(state)

        return {
            "pin": pin_number,
            "state": state,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }

    async def read_imu(self) -> Dict[str, Any]:
        """
        Read IMU (accelerometer and gyroscope) data

        Returns:
            Dictionary containing IMU data
        """
        # Simulate realistic IMU data with some noise
        # Accelerometer in m/s² (gravity + vibration)
        accel_x = 0.0 + random.uniform(-0.5, 0.5)
        accel_y = 0.0 + random.uniform(-0.5, 0.5)
        accel_z = 9.81 + random.uniform(-0.3, 0.3)  # Gravity

        # Gyroscope in rad/s (rotation rates)
        gyro_x = random.uniform(-0.1, 0.1)
        gyro_y = random.uniform(-0.1, 0.1)
        gyro_z = random.uniform(-0.05, 0.05)

        imu_data = IMUData(
            accelerometer={
                "x": round(accel_x, 3),
                "y": round(accel_y, 3),
                "z": round(accel_z, 3),
                "unit": "m/s²"
            },
            gyroscope={
                "x": round(gyro_x, 4),
                "y": round(gyro_y, 4),
                "z": round(gyro_z, 4),
                "unit": "rad/s"
            },
            timestamp=time.time()
        )

        result = imu_data.to_dict()
        result["timestamp"] = datetime.now().isoformat()
        return result

    def _check_temperature_fault(self, sensor_name: str, temperature: float) -> None:
        """Check for temperature faults"""
        if temperature >= self.TEMP_CRITICAL_THRESHOLD:
            fault = Fault(
                FaultType.OVERTEMPERATURE,
                sensor_name,
                temperature,
                self.TEMP_CRITICAL_THRESHOLD,
                datetime.now(),
                "critical"
            )
            self._faults.append(fault)
        elif temperature >= self.TEMP_WARNING_THRESHOLD:
            fault = Fault(
                FaultType.OVERTEMPERATURE,
                sensor_name,
                temperature,
                self.TEMP_WARNING_THRESHOLD,
                datetime.now(),
                "warning"
            )
            self._faults.append(fault)

    def _check_voltage_fault(self, cell_name: str, voltage: float) -> None:
        """Check for voltage faults"""
        if voltage >= self.VOLTAGE_MAX_CRITICAL:
            fault = Fault(
                FaultType.OVERVOLTAGE,
                cell_name,
                voltage,
                self.VOLTAGE_MAX_CRITICAL,
                datetime.now(),
                "critical"
            )
            self._faults.append(fault)
        elif voltage >= self.VOLTAGE_MAX_WARNING:
            fault = Fault(
                FaultType.OVERVOLTAGE,
                cell_name,
                voltage,
                self.VOLTAGE_MAX_WARNING,
                datetime.now(),
                "warning"
            )
            self._faults.append(fault)
        elif voltage <= self.VOLTAGE_MIN_CRITICAL:
            fault = Fault(
                FaultType.UNDERVOLTAGE,
                cell_name,
                voltage,
                self.VOLTAGE_MIN_CRITICAL,
                datetime.now(),
                "critical"
            )
            self._faults.append(fault)
        elif voltage <= self.VOLTAGE_MIN_WARNING:
            fault = Fault(
                FaultType.UNDERVOLTAGE,
                cell_name,
                voltage,
                self.VOLTAGE_MIN_WARNING,
                datetime.now(),
                "warning"
            )
            self._faults.append(fault)

    def _check_current_fault(self, channel_name: str, current: float) -> None:
        """Check for current faults"""
        if current >= self.CURRENT_CRITICAL_THRESHOLD:
            fault = Fault(
                FaultType.OVERCURRENT,
                channel_name,
                current,
                self.CURRENT_CRITICAL_THRESHOLD,
                datetime.now(),
                "critical"
            )
            self._faults.append(fault)
        elif current >= self.CURRENT_WARNING_THRESHOLD:
            fault = Fault(
                FaultType.OVERCURRENT,
                channel_name,
                current,
                self.CURRENT_WARNING_THRESHOLD,
                datetime.now(),
                "warning"
            )
            self._faults.append(fault)

    async def run_fault_detection(self) -> Dict[str, Any]:
        """
        Run comprehensive fault detection across all sensors

        Returns:
            Dictionary containing fault detection results
        """
        # Clear old faults (keep last 100)
        if len(self._faults) > 100:
            self._faults = self._faults[-100:]

        # Read all sensors to trigger fault detection
        for sensor_name in self.temperature_sensors:
            await self.read_temperature(sensor_name)

        for cell_name in self.voltage_cells:
            await self.read_voltage(cell_name)

        for channel_name in self.current_channels:
            await self.read_current(channel_name)

        # Get recent faults (last 10 seconds)
        recent_faults = [
            f for f in self._faults
            if (datetime.now() - f.timestamp).total_seconds() < 10
        ]

        return {
            "total_faults": len(recent_faults),
            "critical_faults": len([f for f in recent_faults if f.severity == "critical"]),
            "warning_faults": len([f for f in recent_faults if f.severity == "warning"]),
            "faults": [f.to_dict() for f in recent_faults],
            "timestamp": datetime.now().isoformat()
        }

    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health status

        Returns:
            Dictionary containing system health information
        """
        # Read all sensors
        temps = {}
        for sensor_name in self.temperature_sensors:
            data = await self.read_temperature(sensor_name)
            temps[sensor_name] = data["temperature_celsius"]

        voltages = {}
        for cell_name in self.voltage_cells:
            data = await self.read_voltage(cell_name)
            voltages[cell_name] = data["voltage"]

        currents = {}
        for channel_name in self.current_channels:
            data = await self.read_current(channel_name)
            currents[channel_name] = data["current"]

        # Calculate health metrics
        avg_temp = sum(temps.values()) / len(temps)
        avg_voltage = sum(voltages.values()) / len(voltages)
        total_current = sum(currents.values())

        # Determine overall health status
        critical_faults = len(
            [f for f in self._faults[-10:] if f.severity == "critical"])
        warning_faults = len(
            [f for f in self._faults[-10:] if f.severity == "warning"])

        if critical_faults > 0:
            health_status = "critical"
        elif warning_faults > 2:
            health_status = "degraded"
        elif warning_faults > 0:
            health_status = "warning"
        else:
            health_status = "healthy"

        uptime = time.time() - self._start_time

        return {
            "status": health_status,
            "uptime_seconds": round(uptime, 2),
            "metrics": {
                "average_temperature": round(avg_temp, 2),
                "average_voltage": round(avg_voltage, 3),
                "total_current": round(total_current, 2)
            },
            "temperatures": temps,
            "voltages": voltages,
            "currents": currents,
            "fault_summary": {
                "critical": critical_faults,
                "warning": warning_faults
            },
            "timestamp": datetime.now().isoformat()
        }


# Global simulator instance
_simulator: Optional[HardwareSimulator] = None


def get_simulator() -> HardwareSimulator:
    """
    Get or create the global hardware simulator instance

    Returns:
        HardwareSimulator instance
    """
    global _simulator
    if _simulator is None:
        _simulator = HardwareSimulator()
    return _simulator

# Made with Bob
