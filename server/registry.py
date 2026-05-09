"""
Device Registry

Reads a YAML hardware profile and holds all device configs for the server.
main.py and backend.py talk to this — never to raw dicts or YAML directly.

Every engineer's hardware is different. This file makes sure the server
knows what's actually plugged in before it starts advertising tools.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import yaml

from server.hal.base import (
    SensorConfig, SensorKind,
    CANBusConfig,
    GPIOConfig, GPIOMode,
    IMUConfig,
)

logger = logging.getLogger(__name__)


class DeviceRegistry:
    """
    Holds everything declared in a YAML profile.

    After load(), the server knows exactly what hardware exists and can
    build its tool list and validate every incoming tool call against it.
    """

    def __init__(self) -> None:
        self.sensors:      dict[str, SensorConfig] = {}
        self.can_buses:    dict[str, CANBusConfig] = {}
        self.gpio_pins:    dict[int,  GPIOConfig]  = {}
        self.imu_devices:  dict[str, IMUConfig]    = {}
        self.profile_name: str = "unloaded"

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self, path: str) -> None:
        """
        Load a YAML profile from disk.

        If the file doesn't exist, falls back to the built-in default
        so the server always starts — even with no config file present.
        This is important for first-time users who just cloned the repo.
        """
        p = Path(path)
        if not p.exists():
            logger.warning(
                "Profile '%s' not found — falling back to built-in default. "
                "Create a YAML profile to describe your hardware.",
                path,
            )
            self._load_default()
            return

        with open(p) as f:
            raw = yaml.safe_load(f)

        self.profile_name = raw.get("name", path)
        self._parse(raw)
        logger.info("Loaded profile '%s'", self.profile_name)

    def load_dict(self, raw: dict) -> None:
        """Load directly from a dict — used in tests."""
        self.profile_name = raw.get("name", "inline")
        self._parse(raw)

    def _parse(self, raw: dict) -> None:
        """Parse raw YAML dict into typed config objects."""
        self.sensors.clear()
        self.can_buses.clear()
        self.gpio_pins.clear()
        self.imu_devices.clear()

        for s in raw.get("sensors", []):
            cfg = SensorConfig(
                id        = s["id"],
                kind      = SensorKind(s["kind"]),
                label     = s.get("label", s["id"]),
                unit      = s.get("unit", ""),
                min_val   = float(s.get("min_val", -1e9)),
                max_val   = float(s.get("max_val",  1e9)),
                warn_high = _opt(s.get("warn_high")),
                crit_high = _opt(s.get("crit_high")),
                warn_low  = _opt(s.get("warn_low")),
                crit_low  = _opt(s.get("crit_low")),
                meta      = s.get("meta", {}),
            )
            self.sensors[cfg.id] = cfg

        for b in raw.get("can_buses", []):
            cfg = CANBusConfig(
                id      = b["id"],
                label   = b.get("label", b["id"]),
                bitrate = int(b.get("bitrate", 500_000)),
                meta    = b.get("meta", {}),
            )
            self.can_buses[cfg.id] = cfg

        for g in raw.get("gpio", []):
            cfg = GPIOConfig(
                pin   = int(g["pin"]),
                mode  = GPIOMode(g.get("mode", "input")),
                label = g.get("label", f"gpio_{g['pin']}"),
                meta  = g.get("meta", {}),
            )
            self.gpio_pins[cfg.pin] = cfg

        for i in raw.get("imu", []):
            cfg = IMUConfig(
                id    = i["id"],
                label = i.get("label", i["id"]),
                meta  = i.get("meta", {}),
            )
            self.imu_devices[cfg.id] = cfg

    def _load_default(self) -> None:
        """
        Built-in fallback — generic sensor names, works out of the box.
        Engineers replace this with their own profile.
        """
        self.load_dict({
            "name": "default-simulator",
            "sensors": [
                {
                    "id": "temp_0", "kind": "temperature",
                    "label": "Temperature Sensor 0", "unit": "celsius",
                    "min_val": -40, "max_val": 150,
                    "warn_high": 80, "crit_high": 100,
                },
                {
                    "id": "voltage_0", "kind": "voltage",
                    "label": "Voltage Channel 0", "unit": "volts",
                    "min_val": 0, "max_val": 60,
                    "warn_low": 10, "crit_low": 8,
                    "warn_high": 55, "crit_high": 58,
                },
                {
                    "id": "current_0", "kind": "current",
                    "label": "Current Channel 0", "unit": "amperes",
                    "min_val": 0, "max_val": 200,
                    "warn_high": 150, "crit_high": 180,
                },
                {
                    "id": "pressure_0", "kind": "pressure",
                    "label": "Pressure Sensor 0", "unit": "bar",
                    "min_val": 0, "max_val": 10,
                    "warn_high": 8, "crit_high": 9.5,
                },
            ],
            "can_buses": [
                {"id": "can0", "label": "CAN Bus 0", "bitrate": 500000},
            ],
            "gpio": [
                {"pin": 0, "mode": "input",  "label": "Digital Input 0"},
                {"pin": 1, "mode": "input",  "label": "Digital Input 1"},
                {"pin": 2, "mode": "output", "label": "Digital Output 0"},
                {"pin": 3, "mode": "output", "label": "Digital Output 1"},
            ],
            "imu": [
                {"id": "imu0", "label": "IMU 0"},
            ],
        })

    # ------------------------------------------------------------------
    # Accessors — raise KeyError with a clean message on bad ID
    # These are called by main.py on every tool call to validate the
    # incoming sensor_id/bus_id/pin before touching the backend.
    # ------------------------------------------------------------------

    def get_sensor(self, sensor_id: str) -> SensorConfig:
        if sensor_id not in self.sensors:
            raise KeyError(
                f"Unknown sensor '{sensor_id}'. "
                f"Available: {sorted(self.sensors.keys())}"
            )
        return self.sensors[sensor_id]

    def get_can_bus(self, bus_id: str) -> CANBusConfig:
        if bus_id not in self.can_buses:
            raise KeyError(
                f"Unknown CAN bus '{bus_id}'. "
                f"Available: {sorted(self.can_buses.keys())}"
            )
        return self.can_buses[bus_id]

    def get_gpio(self, pin: int) -> GPIOConfig:
        if pin not in self.gpio_pins:
            raise KeyError(
                f"Unknown GPIO pin {pin}. "
                f"Available: {sorted(self.gpio_pins.keys())}"
            )
        return self.gpio_pins[pin]

    def get_imu(self, device_id: str) -> IMUConfig:
        if device_id not in self.imu_devices:
            raise KeyError(
                f"Unknown IMU '{device_id}'. "
                f"Available: {sorted(self.imu_devices.keys())}"
            )
        return self.imu_devices[device_id]


# ------------------------------------------------------------------
# Global singleton
# ------------------------------------------------------------------

_registry: Optional[DeviceRegistry] = None


def get_registry() -> DeviceRegistry:
    """
    Return the global DeviceRegistry instance.

    Always call registry.load(path) in main() before the server starts.
    The singleton means every part of the system shares the same loaded
    profile without passing it around as an argument.
    """
    global _registry
    if _registry is None:
        _registry = DeviceRegistry()
    return _registry


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _opt(val) -> float | None:
    """Convert YAML value to float or None. Handles missing keys cleanly."""
    return float(val) if val is not None else None
