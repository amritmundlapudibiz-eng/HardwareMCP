"""
HardwareMCP Server

Universal MCP (Model Context Protocol) server for hardware monitoring and control.
Config-driven — no hardcoded sensors, buses, or pin numbers. Every device is
declared in a YAML profile (see configs/) and the server builds its tool list
dynamically from that profile at startup.

Transport: stdio (compatible with Claude Desktop, Cursor, any MCP client)

Tools exposed (depend on what's in the profile):
  read_sensor        — any scalar sensor: temperature, voltage, current, pressure, …
  read_can           — any CAN bus by bus ID
  read_gpio          — any GPIO pin by pin number
  write_gpio         — any GPIO output pin
  read_imu           — any IMU device by device ID
  run_fault_detection — threshold-based fault scan across all sensors
  get_system_health   — full snapshot: all readings + fault summary + uptime

Environment variables:
  HARDWAREMCP_PROFILE   path to YAML profile  (default: configs/default.yaml)
  HARDWAREMCP_BACKEND   backend to use: "simulator" | "socketcan" | "serial"
                        (default: "simulator")
  HARDWAREMCP_LOG_LEVEL DEBUG | INFO | WARNING  (default: INFO)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from server.hal.base import SensorKind
from server.registry import DeviceRegistry, get_registry
from server.backend import get_backend


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, os.environ.get("HARDWAREMCP_LOG_LEVEL", "INFO")),
    format="%(asctime)s  %(name)s  %(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# MCP app
# ---------------------------------------------------------------------------

app = Server("hardwaremcp")


# ---------------------------------------------------------------------------
# Tool builder  — called at list_tools time so it always reflects the
# currently loaded profile, not a stale module-level constant
# ---------------------------------------------------------------------------

def build_tools(registry: DeviceRegistry) -> list[Tool]:
    """
    Dynamically construct the tool list from whatever is in the registry.

    If a profile has no CAN buses, the read_can tool is not advertised.
    If it has no IMU devices, read_imu is not advertised. Etc.
    This means a client only sees tools that are actually usable.
    """
    tools: list[Tool] = []

    # ------------------------------------------------------------------ #
    # read_sensor — one tool covers ALL scalar sensors regardless of kind #
    # ------------------------------------------------------------------ #
    if registry.sensors:
        sensor_ids = sorted(registry.sensors.keys())
        # Build a richer description that tells the LLM what each sensor is
        sensor_lines = ", ".join(
            f"{s.id} ({s.label}, {s.unit})"
            for s in registry.sensors.values()
        )
        tools.append(Tool(
            name="read_sensor",
            description=(
                "Read a scalar sensor value by ID. "
                f"Available sensors — {sensor_lines}. "
                "Returns: sensor_id, label, value, unit, timestamp. "
                "Temperature sensors also return value_fahrenheit."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sensor_id": {
                        "type": "string",
                        "description": "ID of the sensor to read",
                        "enum": sensor_ids,
                    }
                },
                "required": ["sensor_id"],
            },
        ))

    # ------------------------------------------------------------------ #
    # read_can                                                             #
    # ------------------------------------------------------------------ #
    if registry.can_buses:
        bus_ids = sorted(registry.can_buses.keys())
        bus_lines = ", ".join(
            f"{b.id} ({b.label}, {b.bitrate // 1000}kbps)"
            for b in registry.can_buses.values()
        )
        tools.append(Tool(
            name="read_can",
            description=(
                "Read the next available message from a CAN bus. "
                f"Available buses — {bus_lines}. "
                "Returns: bus_id, arb_id (hex), data (hex bytes), length, timestamp."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "bus_id": {
                        "type": "string",
                        "description": "CAN bus ID to read from",
                        "enum": bus_ids,
                    }
                },
                "required": ["bus_id"],
            },
        ))

    # ------------------------------------------------------------------ #
    # read_gpio / write_gpio                                               #
    # ------------------------------------------------------------------ #
    if registry.gpio_pins:
        pin_numbers = sorted(registry.gpio_pins.keys())
        pin_lines = ", ".join(
            f"pin {p.pin} {p.mode.value} ({p.label})"
            for p in registry.gpio_pins.values()
        )
        tools.append(Tool(
            name="read_gpio",
            description=(
                "Read the current state of a GPIO pin. "
                f"Available pins — {pin_lines}. "
                "Returns: pin, label, mode, state (bool), value (0/1), timestamp."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "pin": {
                        "type": "integer",
                        "description": "GPIO pin number",
                        "enum": pin_numbers,
                    }
                },
                "required": ["pin"],
            },
        ))
        # Only expose write_gpio if at least one output pin exists
        output_pins = sorted(
            p.pin for p in registry.gpio_pins.values() if p.mode.value == "output"
        )
        if output_pins:
            tools.append(Tool(
                name="write_gpio",
                description=(
                    "Set the state of a GPIO output pin. "
                    f"Output pins available: {output_pins}. "
                    "Returns: pin, state, timestamp."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pin": {
                            "type": "integer",
                            "description": "GPIO output pin number",
                            "enum": output_pins,
                        },
                        "state": {
                            "type": "boolean",
                            "description": "Desired pin state: true = HIGH, false = LOW",
                        },
                    },
                    "required": ["pin", "state"],
                },
            ))

    # ------------------------------------------------------------------ #
    # read_imu                                                             #
    # ------------------------------------------------------------------ #
    if registry.imu_devices:
        imu_ids = sorted(registry.imu_devices.keys())
        imu_lines = ", ".join(
            f"{i.id} ({i.label})" for i in registry.imu_devices.values()
        )
        tools.append(Tool(
            name="read_imu",
            description=(
                "Read IMU (accelerometer + gyroscope) data from a device. "
                f"Available devices — {imu_lines}. "
                "Returns: device_id, accel {x,y,z,unit}, gyro {x,y,z,unit}, timestamp."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "IMU device ID",
                        "enum": imu_ids,
                    }
                },
                "required": ["device_id"],
            },
        ))

    # ------------------------------------------------------------------ #
    # run_fault_detection  — always present if there are sensors          #
    # ------------------------------------------------------------------ #
    if registry.sensors:
        tools.append(Tool(
            name="run_fault_detection",
            description=(
                "Run threshold-based fault detection across every registered sensor. "
                "Checks warn_high, crit_high, warn_low, crit_low from the loaded profile. "
                "Returns: total_faults, critical_faults, warning_faults, faults[], timestamp."
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ))

    # ------------------------------------------------------------------ #
    # get_system_health  — always present                                 #
    # ------------------------------------------------------------------ #
    tools.append(Tool(
        name="get_system_health",
        description=(
            "Full system snapshot: reads every sensor, runs fault detection, "
            "reports uptime and loaded profile name. "
            "Returns: status, profile, uptime_seconds, sensors{}, fault_summary{}, timestamp."
        ),
        inputSchema={"type": "object", "properties": {}, "required": []},
    ))

    return tools


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _health_status(faults: list) -> str:
    crits    = sum(1 for f in faults if f.severity == "critical")
    warnings = sum(1 for f in faults if f.severity == "warning")
    if crits    > 0: return "critical"
    if warnings > 2: return "degraded"
    if warnings > 0: return "warning"
    return "healthy"


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return tool list built from the currently loaded device profile."""
    registry = get_registry()
    tools    = build_tools(registry)
    logger.info(
        "list_tools → %d tools for profile '%s'",
        len(tools), registry.profile_name,
    )
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """
    Dispatch an MCP tool call to the active hardware backend.

    All sensor/device IDs are validated against the registry before
    touching the backend — bad IDs get a clean error, not a traceback.
    """
    logger.info("call_tool: %s  args=%s", name, arguments)

    registry = get_registry()
    backend  = get_backend()

    try:
        # ---------------------------------------------------------------- #
        # read_sensor                                                        #
        # ---------------------------------------------------------------- #
        if name == "read_sensor":
            sensor_id = arguments.get("sensor_id")
            if not sensor_id:
                raise ValueError("sensor_id is required")

            cfg     = registry.get_sensor(sensor_id)   # KeyError → clean msg
            reading = await backend.read_sensor(cfg)

            result: Dict[str, Any] = {
                "sensor_id": reading.sensor_id,
                "label":     reading.label,
                "value":     reading.value,
                "unit":      reading.unit,
                "timestamp": reading.timestamp,
            }
            # Bonus fahrenheit for temperature sensors
            if reading.kind == SensorKind.TEMPERATURE:
                result["value_fahrenheit"] = round(reading.value * 9 / 5 + 32, 2)

        # ---------------------------------------------------------------- #
        # read_can                                                           #
        # ---------------------------------------------------------------- #
        elif name == "read_can":
            bus_id = arguments.get("bus_id")
            if not bus_id:
                raise ValueError("bus_id is required")

            cfg     = registry.get_can_bus(bus_id)
            reading = await backend.read_can(cfg)

            result = {
                "bus_id":    reading.bus_id,
                "arb_id":    hex(reading.arb_id),
                "data":      [hex(b) for b in reading.data],
                "length":    len(reading.data),
                "timestamp": reading.timestamp,
            }

        # ---------------------------------------------------------------- #
        # read_gpio                                                          #
        # ---------------------------------------------------------------- #
        elif name == "read_gpio":
            pin = arguments.get("pin")
            if pin is None:
                raise ValueError("pin is required")

            cfg     = registry.get_gpio(int(pin))
            reading = await backend.read_gpio(cfg)

            result = {
                "pin":       reading.pin,
                "label":     reading.label,
                "mode":      reading.mode,
                "state":     reading.state,
                "value":     1 if reading.state else 0,
                "timestamp": reading.timestamp,
            }

        # ---------------------------------------------------------------- #
        # write_gpio                                                         #
        # ---------------------------------------------------------------- #
        elif name == "write_gpio":
            pin   = arguments.get("pin")
            state = arguments.get("state")
            if pin is None:
                raise ValueError("pin is required")
            if state is None:
                raise ValueError("state is required")

            cfg     = registry.get_gpio(int(pin))
            reading = await backend.write_gpio(cfg, bool(state))

            result = {
                "pin":       reading.pin,
                "label":     reading.label,
                "state":     reading.state,
                "value":     1 if reading.state else 0,
                "timestamp": reading.timestamp,
            }

        # ---------------------------------------------------------------- #
        # read_imu                                                           #
        # ---------------------------------------------------------------- #
        elif name == "read_imu":
            device_id = arguments.get("device_id")
            if not device_id:
                raise ValueError("device_id is required")

            cfg     = registry.get_imu(device_id)
            reading = await backend.read_imu(cfg)

            result = {
                "device_id": reading.device_id,
                "accel": {**reading.accel, "unit": reading.accel_unit},
                "gyro":  {**reading.gyro,  "unit": reading.gyro_unit},
                "timestamp": reading.timestamp,
            }

        # ---------------------------------------------------------------- #
        # run_fault_detection                                                #
        # ---------------------------------------------------------------- #
        elif name == "run_fault_detection":
            sensor_cfgs = list(registry.sensors.values())
            readings    = [await backend.read_sensor(c) for c in sensor_cfgs]
            faults      = backend.evaluate_faults(readings, sensor_cfgs)

            result = {
                "total_faults":    len(faults),
                "critical_faults": sum(1 for f in faults if f.severity == "critical"),
                "warning_faults":  sum(1 for f in faults if f.severity == "warning"),
                "faults": [
                    {
                        "sensor_id": f.sensor_id,
                        "type":      f.fault_type,
                        "value":     f.value,
                        "threshold": f.threshold,
                        "severity":  f.severity,
                        "timestamp": f.timestamp,
                    }
                    for f in faults
                ],
                "timestamp": _now_iso(),
            }

        # ---------------------------------------------------------------- #
        # get_system_health                                                  #
        # ---------------------------------------------------------------- #
        elif name == "get_system_health":
            sensor_cfgs = list(registry.sensors.values())
            readings    = [await backend.read_sensor(c) for c in sensor_cfgs]
            faults      = backend.evaluate_faults(readings, sensor_cfgs)

            result = {
                "status":  _health_status(faults),
                "profile": registry.profile_name,
                "uptime_seconds": round(backend.uptime(), 2),
                "sensors": {
                    r.sensor_id: {
                        "label": r.label,
                        "value": r.value,
                        "unit":  r.unit,
                    }
                    for r in readings
                },
                "fault_summary": {
                    "critical": sum(1 for f in faults if f.severity == "critical"),
                    "warning":  sum(1 for f in faults if f.severity == "warning"),
                },
                "timestamp": _now_iso(),
            }

        # ---------------------------------------------------------------- #
        # Unknown tool                                                       #
        # ---------------------------------------------------------------- #
        else:
            raise ValueError(
                f"Unknown tool '{name}'. "
                f"Call list_tools to see what's available for the current profile."
            )

        logger.info("call_tool: %s OK", name)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except (KeyError, ValueError) as e:
        # Expected errors (bad sensor ID, missing arg) — no stack trace needed
        logger.warning("call_tool: %s client error: %s", name, e)
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    except Exception as e:
        # Unexpected backend error — log full trace
        logger.error("call_tool: %s backend error", name, exc_info=True)
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

async def main() -> None:
    """
    Start the HardwareMCP server.

    Startup sequence:
      1. Load device profile from HARDWAREMCP_PROFILE (default: configs/default.yaml)
      2. Connect the hardware backend (simulator or real hardware)
      3. Run the MCP server over stdio until the client disconnects
      4. Cleanly disconnect the backend on shutdown
    """
    profile_path = os.environ.get("HARDWAREMCP_PROFILE", "configs/default.yaml")
    backend_name = os.environ.get("HARDWAREMCP_BACKEND", "simulator")

    logger.info("HardwareMCP starting — profile=%s  backend=%s", profile_path, backend_name)

    # Load device registry from profile
    registry = get_registry()
    registry.load(profile_path)
    logger.info(
        "Profile loaded: '%s'  sensors=%d  can_buses=%d  gpio=%d  imu=%d",
        registry.profile_name,
        len(registry.sensors),
        len(registry.can_buses),
        len(registry.gpio_pins),
        len(registry.imu_devices),
    )

    # Connect backend
    backend = get_backend(backend_name)
    await backend.connect()
    logger.info("Backend '%s' connected", backend_name)

    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("stdio transport ready — waiting for MCP client")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error("Server error: %s", e, exc_info=True)
        raise
    finally:
        await backend.disconnect()
        logger.info("HardwareMCP stopped")


if __name__ == "__main__":
    asyncio.run(main())
