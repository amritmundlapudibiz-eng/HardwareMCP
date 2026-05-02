# HardwareMCP File Structure

## Complete Project Layout

```
HardwareMCP/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # CI/CD pipeline
│   │   ├── release.yml               # Release automation
│   │   └── docker.yml                # Docker build and push
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── server/                           # Main MCP server package
│   ├── __init__.py
│   ├── main.py                       # Entry point and MCP server setup
│   ├── config.py                     # Configuration loader and validator
│   ├── logger.py                     # Logging configuration
│   │
│   ├── mcp/                          # MCP protocol implementation
│   │   ├── __init__.py
│   │   ├── server.py                 # MCP server core
│   │   ├── tools.py                  # Tool definitions and handlers
│   │   ├── resources.py              # Resource definitions and handlers
│   │   ├── prompts.py                # Prompt templates for AI agents
│   │   └── schemas.py                # JSON schemas for validation
│   │
│   ├── hal/                          # Hardware Abstraction Layer
│   │   ├── __init__.py
│   │   ├── interface.py              # Base HAL interface
│   │   ├── manager.py                # Protocol manager factory
│   │   ├── registry.py               # Device registry
│   │   ├── discovery.py              # Auto-discovery logic
│   │   └── exceptions.py             # HAL-specific exceptions
│   │
│   ├── protocols/                    # Protocol implementations
│   │   ├── __init__.py
│   │   ├── base.py                   # Base protocol manager
│   │   │
│   │   ├── gpio/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py            # GPIO protocol manager
│   │   │   ├── driver.py             # Real hardware driver
│   │   │   ├── simulator.py          # GPIO simulator
│   │   │   └── models.py             # Data models
│   │   │
│   │   ├── i2c/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py            # I2C protocol manager
│   │   │   ├── driver.py             # Real hardware driver
│   │   │   ├── simulator.py          # I2C bus simulator
│   │   │   └── models.py             # Data models
│   │   │
│   │   ├── spi/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py            # SPI protocol manager
│   │   │   ├── driver.py             # Real hardware driver
│   │   │   ├── simulator.py          # SPI bus simulator
│   │   │   └── models.py             # Data models
│   │   │
│   │   ├── uart/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py            # UART protocol manager
│   │   │   ├── driver.py             # Real hardware driver
│   │   │   ├── simulator.py          # UART simulator
│   │   │   └── models.py             # Data models
│   │   │
│   │   ├── can/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py            # CAN bus protocol manager
│   │   │   ├── driver.py             # Real hardware driver
│   │   │   ├── simulator.py          # CAN bus simulator
│   │   │   └── models.py             # Data models
│   │   │
│   │   ├── mqtt/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py            # MQTT protocol manager
│   │   │   ├── client.py             # MQTT client wrapper
│   │   │   ├── simulator.py          # MQTT broker simulator
│   │   │   └── models.py             # Data models
│   │   │
│   │   └── modbus/
│   │       ├── __init__.py
│   │       ├── manager.py            # Modbus protocol manager
│   │       ├── driver.py             # Real hardware driver
│   │       ├── simulator.py          # Modbus simulator
│   │       └── models.py             # Data models
│   │
│   ├── simulator/                    # Hardware simulator core
│   │   ├── __init__.py
│   │   ├── core.py                   # Simulator engine
│   │   ├── state.py                  # State management
│   │   ├── devices.py                # Virtual device definitions
│   │   └── scenarios.py              # Test scenarios
│   │
│   ├── devices/                      # High-level device abstractions
│   │   ├── __init__.py
│   │   ├── base.py                   # Base device class
│   │   ├── sensors.py                # Sensor devices
│   │   ├── actuators.py              # Actuator devices
│   │   ├── displays.py               # Display devices
│   │   └── motors.py                 # Motor controllers
│   │
│   └── utils/                        # Utility modules
│       ├── __init__.py
│       ├── validators.py             # Input validation
│       ├── converters.py             # Data type converters
│       ├── timing.py                 # Timing utilities
│       └── platform.py               # Platform detection
│
├── dashboard/                        # Web monitoring dashboard
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── app.py                    # FastAPI application
│   │   ├── websocket.py              # WebSocket handler
│   │   ├── api.py                    # REST API endpoints
│   │   └── models.py                 # API data models
│   │
│   ├── frontend/
│   │   ├── public/
│   │   │   ├── index.html
│   │   │   └── favicon.ico
│   │   │
│   │   ├── src/
│   │   │   ├── App.tsx               # Main React component
│   │   │   ├── index.tsx             # Entry point
│   │   │   │
│   │   │   ├── components/
│   │   │   │   ├── DeviceList.tsx    # Device list view
│   │   │   │   ├── ProtocolView.tsx  # Protocol-specific views
│   │   │   │   ├── DataChart.tsx     # Real-time charts
│   │   │   │   ├── LogViewer.tsx     # Log viewer
│   │   │   │   └── ConfigEditor.tsx  # Configuration editor
│   │   │   │
│   │   │   ├── hooks/
│   │   │   │   ├── useWebSocket.ts   # WebSocket hook
│   │   │   │   └── useHardware.ts    # Hardware state hook
│   │   │   │
│   │   │   ├── services/
│   │   │   │   ├── api.ts            # API client
│   │   │   │   └── websocket.ts      # WebSocket client
│   │   │   │
│   │   │   └── types/
│   │   │       └── hardware.ts       # TypeScript types
│   │   │
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── vite.config.ts
│   │
│   └── README.md
│
├── agent/                            # Example AI agent integrations
│   ├── __init__.py
│   ├── langchain_example.py          # LangChain integration
│   ├── autogen_example.py            # AutoGen integration
│   ├── openai_example.py             # OpenAI function calling
│   ├── anthropic_example.py          # Anthropic Claude integration
│   └── custom_agent.py               # Custom agent template
│
├── examples/                         # Usage examples
│   ├── basic/
│   │   ├── gpio_blink.py             # Simple GPIO example
│   │   ├── i2c_sensor.py             # I2C sensor reading
│   │   ├── spi_display.py            # SPI display control
│   │   └── uart_serial.py            # UART communication
│   │
│   ├── advanced/
│   │   ├── can_logger.py             # CAN bus data logger
│   │   ├── mqtt_bridge.py            # MQTT bridge example
│   │   ├── modbus_controller.py      # Modbus device control
│   │   └── multi_protocol.py         # Multi-protocol coordination
│   │
│   ├── simulator/
│   │   ├── virtual_sensor.py         # Simulated sensor
│   │   ├── test_scenario.py          # Test scenario runner
│   │   └── stress_test.py            # Stress testing
│   │
│   └── configs/
│       ├── raspberry_pi.yaml         # Raspberry Pi config
│       ├── esp32.yaml                # ESP32 config
│       ├── simulator.yaml            # Simulator config
│       └── full_featured.yaml        # All features enabled
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   │
│   ├── unit/
│   │   ├── test_config.py            # Configuration tests
│   │   ├── test_hal.py               # HAL tests
│   │   ├── test_protocols/
│   │   │   ├── test_gpio.py
│   │   │   ├── test_i2c.py
│   │   │   ├── test_spi.py
│   │   │   ├── test_uart.py
│   │   │   ├── test_can.py
│   │   │   ├── test_mqtt.py
│   │   │   └── test_modbus.py
│   │   └── test_simulator.py         # Simulator tests
│   │
│   ├── integration/
│   │   ├── test_mcp_server.py        # MCP server tests
│   │   ├── test_tools.py             # Tool execution tests
│   │   ├── test_resources.py         # Resource tests
│   │   └── test_multi_protocol.py    # Multi-protocol tests
│   │
│   ├── hardware/                     # Hardware-in-loop tests
│   │   ├── test_real_gpio.py
│   │   ├── test_real_i2c.py
│   │   └── README.md                 # Hardware test setup
│   │
│   └── fixtures/
│       ├── configs/                  # Test configurations
│       └── data/                     # Test data files
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md               # Architecture overview
│   ├── FILE_STRUCTURE.md             # This file
│   ├── API_REFERENCE.md              # API documentation
│   ├── CONFIGURATION.md              # Configuration guide
│   ├── PROTOCOLS.md                  # Protocol specifications
│   ├── SIMULATOR.md                  # Simulator guide
│   ├── DEPLOYMENT.md                 # Deployment guide
│   ├── CONTRIBUTING.md               # Contribution guidelines
│   │
│   ├── tutorials/
│   │   ├── getting_started.md
│   │   ├── first_agent.md
│   │   ├── custom_protocol.md
│   │   └── advanced_usage.md
│   │
│   └── images/                       # Documentation images
│       ├── architecture.png
│       └── dashboard.png
│
├── scripts/                          # Utility scripts
│   ├── setup_raspberry_pi.sh         # RPi setup script
│   ├── setup_esp32.sh                # ESP32 setup script
│   ├── install_dependencies.sh       # Dependency installer
│   ├── run_tests.sh                  # Test runner
│   └── generate_docs.py              # Documentation generator
│
├── docker/                           # Docker configurations
│   ├── Dockerfile                    # Main Dockerfile
│   ├── Dockerfile.dev                # Development Dockerfile
│   ├── docker-compose.yml            # Docker Compose config
│   └── entrypoint.sh                 # Container entrypoint
│
├── config/                           # Default configurations
│   ├── default.yaml                  # Default configuration
│   ├── logging.yaml                  # Logging configuration
│   └── schemas/
│       ├── hardware_config.json      # Hardware config schema
│       └── device_types.json         # Device type definitions
│
├── .gitignore
├── .dockerignore
├── .editorconfig
├── .pre-commit-config.yaml           # Pre-commit hooks
├── pyproject.toml                    # Project metadata and dependencies
├── setup.py                          # Setup script
├── requirements.txt                  # Python dependencies
├── requirements-dev.txt              # Development dependencies
├── README.md                         # Project README
├── LICENSE                           # License file
├── CHANGELOG.md                      # Version history
└── MANIFEST.in                       # Package manifest
```

## Module Descriptions

### Server Package (`server/`)

#### Core Modules
- **`main.py`**: Entry point, CLI argument parsing, server initialization
- **`config.py`**: YAML configuration loading, validation, and hot-reload
- **`logger.py`**: Structured logging setup with protocol-specific loggers

#### MCP Layer (`server/mcp/`)
- **`server.py`**: MCP protocol implementation, request/response handling
- **`tools.py`**: Tool definitions (high-level and low-level APIs)
- **`resources.py`**: Resource definitions for streaming hardware data
- **`prompts.py`**: Prompt templates to guide AI agents
- **`schemas.py`**: JSON schemas for request/response validation

#### HAL Layer (`server/hal/`)
- **`interface.py`**: Abstract base classes for protocol managers
- **`manager.py`**: Factory for creating protocol managers
- **`registry.py`**: Device registry with state tracking
- **`discovery.py`**: Auto-discovery for I2C, CAN, and other protocols
- **`exceptions.py`**: Custom exceptions for hardware errors

#### Protocol Implementations (`server/protocols/`)
Each protocol has:
- **`manager.py`**: Protocol-specific manager implementing HAL interface
- **`driver.py`**: Real hardware driver using platform libraries
- **`simulator.py`**: Virtual hardware implementation
- **`models.py`**: Pydantic models for data validation

#### Simulator Core (`server/simulator/`)
- **`core.py`**: Simulator engine coordinating all virtual devices
- **`state.py`**: Centralized state management for virtual hardware
- **`devices.py`**: Virtual device implementations (sensors, actuators)
- **`scenarios.py`**: Predefined test scenarios for automated testing

#### Device Abstractions (`server/devices/`)
- **`base.py`**: Base device class with common functionality
- **`sensors.py`**: High-level sensor abstractions (temperature, pressure, etc.)
- **`actuators.py`**: High-level actuator abstractions (relays, valves)
- **`displays.py`**: Display device abstractions (LCD, OLED)
- **`motors.py`**: Motor controller abstractions (DC, stepper, servo)

#### Utilities (`server/utils/`)
- **`validators.py`**: Input validation functions
- **`converters.py`**: Data type conversion utilities
- **`timing.py`**: Timing and delay utilities
- **`platform.py`**: Platform detection and compatibility

### Dashboard (`dashboard/`)

#### Backend (`dashboard/backend/`)
- **`app.py`**: FastAPI application with CORS and middleware
- **`websocket.py`**: WebSocket server for real-time updates
- **`api.py`**: REST API endpoints for device control
- **`models.py`**: Pydantic models for API requests/responses

#### Frontend (`dashboard/frontend/`)
- **React + TypeScript**: Modern web UI with real-time updates
- **Components**: Modular UI components for different views
- **Hooks**: Custom React hooks for WebSocket and API integration
- **Services**: API and WebSocket client implementations

### Agent Examples (`agent/`)
- **`langchain_example.py`**: Integration with LangChain framework
- **`autogen_example.py`**: Integration with Microsoft AutoGen
- **`openai_example.py`**: Direct OpenAI API with function calling
- **`anthropic_example.py`**: Claude integration with tool use
- **`custom_agent.py`**: Template for custom agent implementations

### Examples (`examples/`)
- **`basic/`**: Simple single-protocol examples
- **`advanced/`**: Complex multi-protocol scenarios
- **`simulator/`**: Simulator-specific examples
- **`configs/`**: Example configuration files for different platforms

### Tests (`tests/`)
- **`unit/`**: Fast, isolated unit tests for each module
- **`integration/`**: Integration tests for MCP server and tools
- **`hardware/`**: Hardware-in-loop tests (require real hardware)
- **`fixtures/`**: Test data and configuration files

### Documentation (`docs/`)
- **Architecture**: System design and component interactions
- **API Reference**: Complete API documentation
- **Configuration**: Configuration file format and options
- **Protocols**: Protocol-specific implementation details
- **Tutorials**: Step-by-step guides for common tasks

### Scripts (`scripts/`)
- **Setup scripts**: Platform-specific setup automation
- **Test runners**: Convenient test execution scripts
- **Documentation generators**: Auto-generate API docs

### Docker (`docker/`)
- **Dockerfile**: Production container image
- **Dockerfile.dev**: Development container with hot-reload
- **docker-compose.yml**: Multi-container orchestration
- **entrypoint.sh**: Container initialization script

## File Naming Conventions

### Python Files
- **Modules**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase` in files named after the main class
- **Tests**: `test_module_name.py`

### Configuration Files
- **YAML**: `lowercase_with_underscores.yaml`
- **JSON**: `lowercase_with_underscores.json`

### Documentation
- **Markdown**: `UPPERCASE_WITH_UNDERSCORES.md` for main docs
- **Tutorials**: `lowercase_with_underscores.md`

## Import Structure

### Absolute Imports
```python
from server.hal.manager import ProtocolManagerFactory
from server.protocols.gpio.manager import GPIOManager
from server.mcp.tools import register_tools
```

### Relative Imports (within package)
```python
from .manager import GPIOManager
from ..base import BaseProtocolManager
```

## Configuration File Locations

### System-wide
- Linux: `/etc/hardwaremcp/config.yaml`
- Windows: `C:\ProgramData\HardwareMCP\config.yaml`

### User-specific
- Linux: `~/.config/hardwaremcp/config.yaml`
- Windows: `%APPDATA%\HardwareMCP\config.yaml`

### Project-specific
- `./config/hardware.yaml` (current directory)
- Path specified via `--config` CLI argument

## Log File Locations

### System-wide
- Linux: `/var/log/hardwaremcp/`
- Windows: `C:\ProgramData\HardwareMCP\logs\`

### User-specific
- Linux: `~/.local/share/hardwaremcp/logs/`
- Windows: `%LOCALAPPDATA%\HardwareMCP\logs\`

## Data Directory Structure

```
~/.local/share/hardwaremcp/  (Linux)
%LOCALAPPDATA%\HardwareMCP\  (Windows)
├── logs/
│   ├── server.log
│   ├── protocols/
│   │   ├── gpio.log
│   │   ├── i2c.log
│   │   └── ...
│   └── dashboard.log
├── state/
│   ├── device_registry.json
│   └── simulator_state.json
└── cache/
    └── discovered_devices.json
```

## Package Distribution Structure

```
hardwaremcp-x.y.z/
├── hardwaremcp/              # Renamed from 'server' for pip package
│   ├── __init__.py
│   ├── __main__.py           # CLI entry point
│   └── [all server modules]
├── dashboard/
├── examples/
├── docs/
├── tests/
├── setup.py
├── pyproject.toml
├── README.md
├── LICENSE
└── MANIFEST.in
```

## Development Workflow Files

### Git
- `.gitignore`: Ignore build artifacts, logs, cache
- `.gitattributes`: Line ending configuration

### Pre-commit
- `.pre-commit-config.yaml`: Code formatting, linting, type checking

### CI/CD
- `.github/workflows/ci.yml`: Run tests on push/PR
- `.github/workflows/release.yml`: Automated releases
- `.github/workflows/docker.yml`: Docker image builds

### IDE
- `.vscode/settings.json`: VSCode settings
- `.vscode/launch.json`: Debug configurations
- `.idea/`: PyCharm settings (gitignored)

## Size Estimates

### Core Server Package
- Python code: ~15,000 lines
- Configuration: ~500 lines
- Total size: ~2-3 MB

### Dashboard
- Frontend: ~5,000 lines TypeScript/React
- Backend: ~1,000 lines Python
- Built assets: ~500 KB

### Documentation
- Markdown: ~10,000 words
- Images: ~2 MB

### Tests
- Test code: ~8,000 lines
- Fixtures: ~1 MB

### Total Repository
- Uncompressed: ~10-15 MB
- Compressed (git): ~3-5 MB