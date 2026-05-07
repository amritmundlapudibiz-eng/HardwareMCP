# HardwareMCP

Universal MCP (Model Context Protocol) server that lets AI agents monitor and control physical hardware. Works with any sensor, CAN bus, GPIO, or IMU — configured via a YAML profile, no code changes required.

Built for embedded engineers, robotics teams, and hardtech companies who want to connect LLMs to real hardware.

---

## How it works

You define your hardware in a YAML profile. The server reads it at startup and exposes only the tools that match your actual devices. A Raspberry Pi hobbyist, an industrial automation engineer, and an EV team all use the same server — just different profiles.
---

## Features

- **Config-driven** — sensors, CAN buses, GPIO pins, and IMUs declared in YAML. No hardcoded hardware.
- **Generic tools** — `read_sensor`, `read_can`, `read_gpio`, `write_gpio`, `read_imu`. Works for any device.
- **Threshold-based fault detection** — warn/critical thresholds per sensor, defined in the profile.
- **Built-in simulator** — test your profile without real hardware.
- **LLM-agnostic** — works with Claude, GPT, Gemini, or any MCP-compatible client.
- **Transport: stdio** — compatible with Claude Desktop, Cursor, and any MCP client out of the box.

---

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`

---

## Quick Start

**1. Clone the repo**
```bash
git clone https://github.com/amritmundlapudibiz-eng/HardwareMCP.git
cd HardwareMCP
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run with the default simulator profile**
```bash
python -m server.main
```

**4. Or load your own profile**
```bash
HARDWAREMCP_PROFILE=configs/my_device.yaml python -m server.main
```

---

## Writing a Profile

A profile is a YAML file that declares your hardware. Every field maps directly to a tool argument — no code changes needed.

```yaml
name: my-robot

sensors:
  - id: motor_temp
    kind: temperature
    label: Motor Temperature
    unit: celsius
    min_val: -20
    max_val: 150
    warn_high: 80
    crit_high: 100

  - id: bus_voltage
    kind: voltage
    label: Main Bus Voltage
    unit: volts
    min_val: 0
    max_val: 60
    warn_low: 10
    crit_low: 8

  - id: phase_current
    kind: current
    label: Phase Current
    unit: amperes
    min_val: 0
    max_val: 200
    warn_high: 150
    crit_high: 180

can_buses:
  - id: can0
    label: Vehicle CAN
    bitrate: 500000

gpio:
  - pin: 17
    mode: input
    label: Limit Switch
  - pin: 27
    mode: output
    label: Relay Control

imu:
  - id: imu0
    label: Main IMU
```

Supported sensor kinds: `temperature`, `voltage`, `current`, `pressure`, `humidity`, `generic`

---

## MCP Tools

Tools are built dynamically from your profile. If your profile has no IMU, `read_imu` is not advertised. If there are no output pins, `write_gpio` is not advertised.

| Tool | Description |
|---|---|
| `read_sensor` | Read any scalar sensor by `sensor_id` |
| `read_can` | Read a CAN frame by `bus_id` |
| `read_gpio` | Read a GPIO pin by `pin` number |
| `write_gpio` | Set a GPIO output pin state |
| `read_imu` | Read accelerometer + gyroscope by `device_id` |
| `run_fault_detection` | Scan all sensors against profile thresholds |
| `get_system_health` | Full snapshot: all readings, faults, uptime |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `HARDWAREMCP_PROFILE` | `configs/default.yaml` | Path to your YAML device profile |
| `HARDWAREMCP_BACKEND` | `simulator` | Backend: `simulator` \| `socketcan` \| `serial` |
| `HARDWAREMCP_LOG_LEVEL` | `INFO` | Log level: `DEBUG` \| `INFO` \| `WARNING` |

---

## Claude Desktop Integration

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hardwaremcp": {
      "command": "python",
      "args": ["-m", "server.main"],
      "cwd": "/path/to/HardwareMCP",
      "env": {
        "HARDWAREMCP_PROFILE": "configs/my_device.yaml"
      }
    }
  }
}
```

---

## Architecture
HardwareMCP/
├── server/
│   ├── main.py          # MCP server — tool builder + dispatcher
│   ├── registry.py      # Loads YAML profiles, holds device configs
│   ├── backend.py       # Backend factory (simulator / real hardware)
│   └── hal/
│       ├── base.py      # Abstract HAL interface all backends implement
│       └── simulator.py # Generic simulator — no hardcoded hardware
├── configs/
│   ├── default.yaml     # Generic fallback profile
│   ├── raspberry_pi.yaml
│   └── industrial.yaml
├── tests/
│   └── test_simulator.py
└── requirements.txt

---

## Adding a Real Hardware Backend

1. Subclass `HardwareBackend` from `server/hal/base.py`
2. Implement `connect`, `disconnect`, `read_sensor`, `read_can`, `read_gpio`, `write_gpio`, `read_imu`
3. Register it in `server/backend.py`
4. Set `HARDWAREMCP_BACKEND=your_backend`

The simulator and real backends share the same interface — swapping is one env var change.

---

## Testing

```bash
pytest tests/ -v --tb=short
pytest tests/ --cov=server --cov-report=html
```

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Add a YAML profile or backend for your hardware
4. Ensure tests pass
5. Open a PR

Community-contributed profiles for common hardware (Raspberry Pi, Arduino, industrial PLCs, robotics platforms) are especially welcome.

---

## License

MIT
