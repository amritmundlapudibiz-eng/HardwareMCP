# HardwareMCP Dependencies

## Python Version
- **Minimum**: Python 3.10+
- **Recommended**: Python 3.11+ for better performance
- **Type Hints**: Full type hint support required

## Core Dependencies

### MCP Protocol
```toml
mcp = "^1.0.0"                    # Model Context Protocol SDK
pydantic = "^2.5.0"               # Data validation and settings
```

### Web Framework (Dashboard)
```toml
fastapi = "^0.109.0"              # Modern web framework
uvicorn = "^0.27.0"               # ASGI server
websockets = "^12.0"              # WebSocket support
python-multipart = "^0.0.6"       # File upload support
```

### Configuration & Validation
```toml
pyyaml = "^6.0.1"                 # YAML parsing
jsonschema = "^4.20.0"            # JSON schema validation
python-dotenv = "^1.0.0"          # Environment variables
```

### Logging & Monitoring
```toml
structlog = "^24.1.0"             # Structured logging
rich = "^13.7.0"                  # Beautiful terminal output
prometheus-client = "^0.19.0"     # Metrics collection
```

### Async & Concurrency
```toml
asyncio = "built-in"              # Async I/O
aiofiles = "^23.2.1"              # Async file operations
aioconsole = "^0.7.0"             # Async console I/O
```

## Protocol-Specific Dependencies

### GPIO (Raspberry Pi)
```toml
RPi.GPIO = "^0.7.1"               # Raspberry Pi GPIO (optional)
gpiod = "^2.1.0"                  # Modern GPIO interface (optional)
lgpio = "^0.2.2.0"                # Alternative GPIO library (optional)
```

### I2C
```toml
smbus2 = "^0.4.3"                 # I2C/SMBus library (optional)
adafruit-circuitpython-busdevice = "^5.2.6"  # I2C device helpers (optional)
```

### SPI
```toml
spidev = "^3.6"                   # SPI interface (optional)
adafruit-circuitpython-busdevice = "^5.2.6"  # SPI device helpers (optional)
```

### UART/Serial
```toml
pyserial = "^3.5"                 # Serial port access (optional)
pyserial-asyncio = "^0.6"         # Async serial support (optional)
```

### CAN Bus
```toml
python-can = "^4.3.1"             # CAN bus library (optional)
can-isotp = "^2.0.0"              # ISO-TP protocol (optional)
```

### MQTT
```toml
paho-mqtt = "^1.6.1"              # MQTT client (optional)
aiomqtt = "^2.0.0"                # Async MQTT client (optional)
```

### Modbus
```toml
pymodbus = "^3.6.0"               # Modbus protocol (optional)
```

## Platform-Specific Dependencies

### Raspberry Pi
```toml
RPi.GPIO = "^0.7.1"
smbus2 = "^0.4.3"
spidev = "^3.6"
```

### ESP32 (MicroPython)
```toml
# Note: ESP32 uses MicroPython, not CPython
# Dependencies are managed differently
micropython-machine = "*"
micropython-network = "*"
```

### Linux (Generic)
```toml
python-periphery = "^2.4.1"       # GPIO, I2C, SPI, Serial
pyftdi = "^0.55.0"                # FTDI USB devices
```

### Windows
```toml
pyserial = "^3.5"                 # Serial port support
pyftdi = "^0.55.0"                # USB devices
```

## Development Dependencies

### Testing
```toml
pytest = "^7.4.4"                 # Test framework
pytest-asyncio = "^0.23.3"        # Async test support
pytest-cov = "^4.1.0"             # Coverage reporting
pytest-mock = "^3.12.0"           # Mocking utilities
pytest-timeout = "^2.2.0"         # Test timeouts
hypothesis = "^6.96.0"            # Property-based testing
```

### Code Quality
```toml
ruff = "^0.1.14"                  # Fast Python linter
black = "^24.1.0"                 # Code formatter
isort = "^5.13.2"                 # Import sorting
mypy = "^1.8.0"                   # Static type checker
pylint = "^3.0.3"                 # Code analysis
```

### Documentation
```toml
mkdocs = "^1.5.3"                 # Documentation generator
mkdocs-material = "^9.5.6"        # Material theme
mkdocstrings = "^0.24.0"          # API doc generation
mkdocstrings-python = "^1.8.0"    # Python handler
```

### Pre-commit Hooks
```toml
pre-commit = "^3.6.0"             # Git hook framework
```

### Build & Release
```toml
build = "^1.0.3"                  # Build tool
twine = "^4.0.2"                  # PyPI upload
bump2version = "^1.0.1"           # Version bumping
```

## Dashboard Frontend Dependencies

### Core Framework
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.3.3"
}
```

### Build Tools
```json
{
  "vite": "^5.0.11",
  "@vitejs/plugin-react": "^4.2.1"
}
```

### UI Components
```json
{
  "@mui/material": "^5.15.6",
  "@mui/icons-material": "^5.15.6",
  "@emotion/react": "^11.11.3",
  "@emotion/styled": "^11.11.0"
}
```

### Data Visualization
```json
{
  "recharts": "^2.10.4",
  "react-flow-renderer": "^10.3.17"
}
```

### State Management
```json
{
  "zustand": "^4.5.0"
}
```

### WebSocket & API
```json
{
  "axios": "^1.6.5",
  "socket.io-client": "^4.6.1"
}
```

### Development
```json
{
  "@types/react": "^18.2.48",
  "@types/react-dom": "^18.2.18",
  "eslint": "^8.56.0",
  "prettier": "^3.2.4"
}
```

## Optional Dependencies by Use Case

### Minimal Installation (Simulator Only)
```bash
pip install hardwaremcp[simulator]
```
Dependencies: Core + Simulator only

### Raspberry Pi Installation
```bash
pip install hardwaremcp[raspberry-pi]
```
Dependencies: Core + RPi.GPIO + smbus2 + spidev

### Full Installation (All Protocols)
```bash
pip install hardwaremcp[all]
```
Dependencies: All protocol libraries

### Development Installation
```bash
pip install hardwaremcp[dev]
```
Dependencies: All + testing + linting + docs

### Dashboard Installation
```bash
pip install hardwaremcp[dashboard]
```
Dependencies: Core + FastAPI + WebSocket

## Dependency Groups in pyproject.toml

```toml
[project.optional-dependencies]
# Simulator only (no hardware dependencies)
simulator = []

# Raspberry Pi specific
raspberry-pi = [
    "RPi.GPIO>=0.7.1",
    "smbus2>=0.4.3",
    "spidev>=3.6",
]

# ESP32 specific (for host-side tools)
esp32 = [
    "esptool>=4.7.0",
    "adafruit-ampy>=1.1.0",
]

# All protocol support
protocols = [
    "pyserial>=3.5",
    "python-can>=4.3.1",
    "paho-mqtt>=1.6.1",
    "pymodbus>=3.6.0",
]

# Dashboard
dashboard = [
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "websockets>=12.0",
]

# All features
all = [
    "hardwaremcp[raspberry-pi]",
    "hardwaremcp[protocols]",
    "hardwaremcp[dashboard]",
]

# Development
dev = [
    "hardwaremcp[all]",
    "pytest>=7.4.4",
    "pytest-asyncio>=0.23.3",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.14",
    "black>=24.1.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
]

# Documentation
docs = [
    "mkdocs>=1.5.3",
    "mkdocs-material>=9.5.6",
    "mkdocstrings>=0.24.0",
]
```

## System Dependencies

### Raspberry Pi
```bash
# I2C tools
sudo apt-get install i2c-tools libi2c-dev

# SPI tools
sudo apt-get install python3-spidev

# CAN bus
sudo apt-get install can-utils

# Build tools
sudo apt-get install python3-dev build-essential
```

### Ubuntu/Debian
```bash
# Serial port access
sudo apt-get install python3-serial

# USB device access
sudo apt-get install libusb-1.0-0-dev

# Build tools
sudo apt-get install python3-dev build-essential
```

### macOS
```bash
# Homebrew packages
brew install libusb

# Python build tools
xcode-select --install
```

### Windows
```powershell
# Visual C++ Build Tools (for compiling extensions)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# USB drivers (if needed)
# Download from device manufacturer
```

## Docker Base Images

### Production Image
```dockerfile
FROM python:3.11-slim-bullseye
```

### Development Image
```dockerfile
FROM python:3.11-bullseye
```

### Raspberry Pi Image
```dockerfile
FROM balenalib/raspberry-pi-python:3.11
```

## Version Pinning Strategy

### Core Dependencies
- **Pinned**: MCP SDK, Pydantic (breaking changes possible)
- **Flexible**: Utilities, logging (minor updates safe)

### Protocol Libraries
- **Flexible**: Allow minor updates for bug fixes
- **Test**: Verify compatibility in CI/CD

### Development Tools
- **Latest**: Always use latest for best features
- **Pinned in CI**: Lock versions for reproducible builds

## Dependency Installation Order

1. **Core Python packages**: pydantic, pyyaml
2. **MCP SDK**: mcp
3. **Web framework**: fastapi, uvicorn (if dashboard enabled)
4. **Protocol libraries**: Based on platform and configuration
5. **Development tools**: Only in dev environment

## Conflict Resolution

### Known Conflicts
- `RPi.GPIO` vs `gpiod`: Use only one GPIO library
- `paho-mqtt` vs `aiomqtt`: aiomqtt wraps paho-mqtt
- `pymodbus` versions: Use 3.x for async support

### Resolution Strategy
1. Prefer async-compatible libraries
2. Use platform detection to install correct library
3. Provide clear error messages for conflicts

## Security Considerations

### Dependency Scanning
```bash
# Check for vulnerabilities
pip-audit

# Update dependencies
pip install --upgrade hardwaremcp
```

### Trusted Sources
- PyPI for Python packages
- npm for JavaScript packages
- Official hardware vendor repositories

### Version Constraints
- Minimum versions for security patches
- Maximum versions to avoid breaking changes
- Regular dependency updates in CI/CD

## Performance Considerations

### Heavy Dependencies
- **Avoid**: Large ML libraries unless needed
- **Lazy Load**: Import protocol libraries only when used
- **Optional**: Make heavy dependencies optional

### Startup Time
- Core dependencies: <1 second import time
- Protocol libraries: Lazy loaded on first use
- Dashboard: Separate process, doesn't affect server

## License Compatibility

### Core Dependencies
- **MIT**: Most dependencies (compatible)
- **Apache 2.0**: Some protocol libraries (compatible)
- **LGPL**: Some hardware libraries (compatible with dynamic linking)

### Incompatible Licenses
- **GPL**: Avoid unless necessary
- **Proprietary**: Not used

## Maintenance Schedule

### Regular Updates
- **Monthly**: Check for security updates
- **Quarterly**: Update minor versions
- **Annually**: Consider major version upgrades

### Deprecation Policy
- **6 months notice**: Before removing dependencies
- **Migration guide**: Provided for breaking changes
- **Backward compatibility**: Maintained for 2 major versions