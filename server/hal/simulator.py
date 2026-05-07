"""
HardwareMCP — Generic Hardware Simulator

A config-driven simulator that works with ANY hardware profile.
No hardcoded sensor names, no hardcoded CAN IDs, no FSAE assumptions.

Physics model:
  - Each sensor simulates realistic noise + sinusoidal drift around
    the midpoint of its declared [min_val, max_val] range.
  - CAN frames are randomised 8-byte payloads keyed to the bus config.
  - GPIO inputs toggle randomly (10% chance per read) to simulate real signals.
  - IMU simulates gravity on Z-axis + small vibration noise.

To add a new sensor, add it to your YAML profile — no code changes needed.
"""

from __future__ import annotations

import math
import random
import time
from datetime import datetime, timezone
from typing import Optional

from server.hal.base import (
    HardwareBackend,
    SensorConfig,
    SensorKind,
    SensorReading,
    CANBusConfig,
    CANReading,
    GPIOConfig,
    GPIOMode,
    GPIOReading,
    IMUConfig,
    IMUReading,
    FaultRecord,
)


# ---------------------------------------------------------------------------
# Internal state — lazily created per sensor/pin/device
# ---------------------------------------------------------------------------

class _SensorState:
    """
    Runtime simulation state for one scalar sensor.

    Derives all physics (noise, drift, midpoint) from the SensorConfig
    min/max — works for temperature, voltage, current, pressure, anything.
    No sensor names are hardcoded here.
    """

    def __init__(self, cfg: SensorConfig) -> None:
        self.cfg = cfg
        lo = cfg.min_val if cfg.min_val > -1e8 else 0.0
        hi = cfg.max_val if cfg.max_val <  1e8 else 100.0
        self._mid       = (lo + hi) / 2
        self._span      = (hi - lo) / 2
        self._noise     = self._span * 0.02   # 2% of range as noise
        self._drift_amp = self._span * 0.05   # 5% of range as drift
        # Unique phase per sensor so readings don't all drift in sync
        self._phase     = random.uniform(0, 2 * math.pi)

    def read(self) -> float:
        t     = time.time()
        noise = random.uniform(-self._noise, self._noise)
        drift = math.sin(t / 60 + self._phase) * self._drift_amp
        raw   = self._mid + noise + drift
        return round(max(self.cfg.min_val, min(self.cfg.max_val, raw)), 3)


class _GPIOState:
    """Runtime state for one GPIO pin."""

    def __init__(self, cfg: GPIOConfig) -> None:
        self.cfg   = cfg
        self.state = False

    def read(self) -> bool:
        if self.cfg.mode == GPIOMode.INPUT:
            if random.random() < 0.10:   # 10% chance of toggle per read
                self.state = not self.state
        return self.state

    def write(self, state: bool) -> None:
        if self.cfg.mode != GPIOMode.OUTPUT:
            raise ValueError(
                f"Pin {self.cfg.pin} ({self.cfg.label}) is "
                f"{self.cfg.mode.value} — cannot write to it"
            )
        self.state = state


# ---------------------------------------------------------------------------
# SimulatorBackend
# ---------------------------------------------------------------------------

class SimulatorBackend(HardwareBackend):
    """
    Generic simulator backend — no real hardware required.

    All internal state is lazily initialised on first access, keyed by
    sensor ID / pin number / device ID from the config. Adding a new sensor
    to a YAML profile requires zero changes here.
    """

    def __init__(self) -> None:
        self._sensors:    dict[str, _SensorState] = {}
        self._gpio:       dict[int,  _GPIOState]  = {}
        self._start_time: float = 0.0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        self._start_time = time.time()

    async def disconnect(self) -> None:
        self._sensors.clear()
        self._gpio.clear()

    def uptime(self) -> float:
        return time.time() - self._start_time

    # ------------------------------------------------------------------
    # Lazy state accessors
    # ------------------------------------------------------------------

    def _sensor_state(self, cfg: SensorConfig) -> _SensorState:
        if cfg.id not in self._sensors:
            self._sensors[cfg.id] = _SensorState(cfg)
        return self._sensors[cfg.id]

    def _gpio_state(self, cfg: GPIOConfig) -> _GPIOState:
        if cfg.pin not in self._gpio:
            self._gpio[cfg.pin] = _GPIOState(cfg)
        return self._gpio[cfg.pin]

    # ------------------------------------------------------------------
    # Scalar sensors
    # ------------------------------------------------------------------

    async def read_sensor(self, cfg: SensorConfig) -> SensorReading:
        """
        Read any scalar sensor — temperature, voltage, current, pressure, etc.
        The simulation physics are derived entirely from cfg.min_val/max_val.
        """
        value = self._sensor_state(cfg).read()
        return SensorReading(
            sensor_id = cfg.id,
            kind      = cfg.kind,
            value     = value,
            unit      = cfg.unit,
            label     = cfg.label,
            timestamp = datetime.now(timezone.utc).isoformat(),
        )

    # ------------------------------------------------------------------
    # CAN bus
    # ------------------------------------------------------------------

    async def read_can(self, cfg: CANBusConfig) -> CANReading:
        """
        Simulate a CAN frame on any bus.

        Arbitration ID is randomly selected from the standard 11-bit range.
        Data is 8 random bytes. No Cascadia-specific IDs hardcoded.
        Real profiles that need specific CAN decode logic should use a
        real backend (socketcan) — the simulator just proves the plumbing works.
        """
        arb_id = random.randint(0x001, 0x7FF)   # standard 11-bit CAN ID
        data   = [random.randint(0x00, 0xFF) for _ in range(8)]
        return CANReading(
            bus_id    = cfg.id,
            arb_id    = arb_id,
            data      = data,
            timestamp = time.time(),
        )

    # ------------------------------------------------------------------
    # GPIO
    # ------------------------------------------------------------------

    async def read_gpio(self, cfg: GPIOConfig) -> GPIOReading:
        state = self._gpio_state(cfg).read()
        return GPIOReading(
            pin       = cfg.pin,
            mode      = cfg.mode,
            state     = state,
            label     = cfg.label,
            timestamp = datetime.now(timezone.utc).isoformat(),
        )

    async def write_gpio(self, cfg: GPIOConfig, state: bool) -> GPIOReading:
        gs = self._gpio_state(cfg)
        gs.write(state)   # raises ValueError if not OUTPUT
        return GPIOReading(
            pin       = cfg.pin,
            mode      = cfg.mode,
            state     = gs.state,
            label     = cfg.label,
            timestamp = datetime.now(timezone.utc).isoformat(),
        )

    # ------------------------------------------------------------------
    # IMU
    # ------------------------------------------------------------------

    async def read_imu(self, cfg: IMUConfig) -> IMUReading:
        """
        Simulate a 6-DOF IMU.

        Gravity on Z-axis (9.81 m/s²) + small random vibration.
        Works for any IMU device ID — no device-specific hardcoding.
        """
        return IMUReading(
            device_id  = cfg.id,
            accel      = {
                "x": round(random.uniform(-0.5,  0.5),  3),
                "y": round(random.uniform(-0.5,  0.5),  3),
                "z": round(9.81 + random.uniform(-0.3, 0.3), 3),
            },
            gyro       = {
                "x": round(random.uniform(-0.10, 0.10), 4),
                "y": round(random.uniform(-0.10, 0.10), 4),
                "z": round(random.uniform(-0.05, 0.05), 4),
            },
            accel_unit = "m/s²",
            gyro_unit  = "rad/s",
            timestamp  = datetime.now(timezone.utc).isoformat(),
        )

    # ------------------------------------------------------------------
    # Fault detection  (inherited from HardwareBackend — pure threshold eval)
    # ------------------------------------------------------------------
    # evaluate_faults() is already implemented in base.HardwareBackend.
    # No override needed — the base class handles all threshold logic
    # using warn_high/crit_high/warn_low/crit_low from each SensorConfig.


# ---------------------------------------------------------------------------
# Global instance + factory
# ---------------------------------------------------------------------------

_instance: Optional[SimulatorBackend] = None


def get_simulator() -> SimulatorBackend:
    """Return the global SimulatorBackend instance, creating it if needed."""
    global _instance
    if _instance is None:
        _instance = SimulatorBackend()
    return _instance
