# HardwareMCP - Hardware Monitoring via Model Context Protocol

A production-ready MCP (Model Context Protocol) server for hardware monitoring and control, featuring AI-powered analysis using xAI Grok.

## 🚀 Features

- **8 Hardware Monitoring Tools**:
  - Temperature sensors (engine, battery, ambient, motor)
  - Voltage monitoring (4 battery cells)
  - Current measurement (motor, BMS, auxiliary)
  - CAN bus message reading (Cascadia CM200DZ inverter)
  - GPIO pin control
  - IMU data (accelerometer & gyroscope)
  - Fault detection system
  - System health monitoring

- **Production-Ready Code**:
  - Full type hints and docstrings
  - Comprehensive error handling
  - Async/await support
  - Extensive unit tests (532 lines)
  - Realistic hardware simulation

- **AI Integration**:
  - xAI Grok-powered analysis
  - Intelligent fault detection
  - Automated health reports
  - Natural language insights

## 📋 Requirements

- Python 3.10+
- xAI API key (for AI agent features)

## 🔧 Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/HardwareMCP.git
cd HardwareMCP
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (for AI agent):
```bash
export XAI_API_KEY="your-xai-api-key-here"
```

## 🎯 Quick Start

### Running the MCP Server

Start the HardwareMCP server:

```bash
python -m server.main
```

The server uses stdio transport and will communicate via standard input/output.

### Using the AI Agent

Run the comprehensive hardware analysis agent:

```bash
python agent/gemini_agent.py
```

This will:
1. Check system health
2. Run fault detection
3. Monitor temperatures
4. Analyze battery health
5. Examine CAN bus messages
6. Generate an executive summary

### Running Tests

Execute the test suite:

```bash
pytest tests/test_simulator.py -v
```

Run with coverage:

```bash
pytest tests/test_simulator.py --cov=server.hal --cov-report=html
```

## 📚 API Reference

### MCP Tools

#### 1. read_temperature
Read temperature from a sensor.

**Parameters**:
- `sensor_name` (string): One of "engine", "battery", "ambient", "motor"

**Returns**:
```json
{
  "sensor": "engine",
  "temperature_celsius": 85.23,
  "temperature_fahrenheit": 185.41,
  "timestamp": "2026-05-02T20:00:00.000Z",
  "unit": "celsius"
}
```

#### 2. read_voltage
Read voltage from a battery cell.

**Parameters**:
- `cell_name` (string): One of "cell_1", "cell_2", "cell_3", "cell_4"

**Returns**:
```json
{
  "cell": "cell_1",
  "voltage": 3.702,
  "timestamp": "2026-05-02T20:00:00.000Z",
  "unit": "volts"
}
```

#### 3. read_current
Read current from a channel.

**Parameters**:
- `channel_name` (string): One of "motor", "bms", "aux"

**Returns**:
```json
{
  "channel": "motor",
  "current": 45.67,
  "timestamp": "2026-05-02T20:00:00.000Z",
  "unit": "amperes"
}
```

#### 4. read_can_message
Read a CAN bus message from the Cascadia CM200DZ inverter.

**Parameters**: None

**Returns**:
```json
{
  "source": "Cascadia CM200DZ",
  "message": {
    "can_id": "0xc0",
    "data": ["0x12", "0x34", "0x56", "0x78", "0x9a", "0xbc", "0xde", "0xf0"],
    "timestamp": 1714680000.123,
    "length": 8
  },
  "timestamp": "2026-05-02T20:00:00.000Z"
}
```

#### 5. read_gpio
Read GPIO pin state.

**Parameters**:
- `pin_number` (integer): Pin number 0-5

**Returns**:
```json
{
  "pin": 2,
  "mode": "output",
  "state": true,
  "value": 1,
  "timestamp": "2026-05-02T20:00:00.000Z"
}
```

#### 6. read_imu
Read IMU (accelerometer and gyroscope) data.

**Parameters**: None

**Returns**:
```json
{
  "accelerometer": {
    "x": 0.123,
    "y": -0.045,
    "z": 9.812,
    "unit": "m/s²"
  },
  "gyroscope": {
    "x": 0.0012,
    "y": -0.0034,
    "z": 0.0001,
    "unit": "rad/s"
  },
  "timestamp": "2026-05-02T20:00:00.000Z"
}
```

#### 7. run_fault_detection
Run comprehensive fault detection.

**Parameters**: None

**Returns**:
```json
{
  "total_faults": 2,
  "critical_faults": 1,
  "warning_faults": 1,
  "faults": [
    {
      "type": "overtemperature",
      "sensor": "engine",
      "value": 105.3,
      "threshold": 100.0,
      "timestamp": "2026-05-02T20:00:00.000Z",
      "severity": "critical"
    }
  ],
  "timestamp": "2026-05-02T20:00:00.000Z"
}
```

#### 8. get_system_health
Get overall system health status.

**Parameters**: None

**Returns**:
```json
{
  "status": "healthy",
  "uptime_seconds": 3600.5,
  "metrics": {
    "average_temperature": 52.3,
    "average_voltage": 3.705,
    "total_current": 52.5
  },
  "temperatures": {
    "engine": 85.2,
    "battery": 35.1,
    "ambient": 25.0,
    "motor": 65.3
  },
  "voltages": {
    "cell_1": 3.702,
    "cell_2": 3.715,
    "cell_3": 3.698,
    "cell_4": 3.705
  },
  "currents": {
    "motor": 45.6,
    "bms": 2.4,
    "aux": 4.5
  },
  "fault_summary": {
    "critical": 0,
    "warning": 0
  },
  "timestamp": "2026-05-02T20:00:00.000Z"
}
```

## 🏗️ Architecture

```
HardwareMCP/
├── server/
│   ├── main.py              # MCP server implementation
│   └── hal/
│       └── simulator.py     # Hardware simulator
├── agent/
│   └── gemini_agent.py      # xAI Grok AI agent
├── tests/
│   └── test_simulator.py    # Unit tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🧪 Testing

The project includes comprehensive unit tests covering:

- All 8 MCP tools
- Temperature, voltage, and current sensors
- CAN bus message generation
- GPIO pin operations
- IMU data generation
- Fault detection logic
- System health monitoring
- Edge cases and error handling

Run tests:
```bash
pytest tests/ -v --tb=short
```

## 🤖 AI Agent Usage

The AI agent demonstrates how to:

1. **Connect to MCP Server**: Query hardware through MCP tools
2. **Analyze Data**: Use Grok to interpret sensor readings
3. **Detect Anomalies**: Identify potential issues automatically
4. **Generate Reports**: Create human-readable summaries

Example usage:

```python
from agent.gemini_agent import HardwareMCPAgent

agent = HardwareMCPAgent(api_key="your-key")
await agent.run_comprehensive_analysis()
```

## 🔒 Fault Detection

The system automatically detects:

- **Overtemperature**: Warning at 80°C, Critical at 100°C
- **Overvoltage**: Warning at 4.1V, Critical at 4.3V
- **Undervoltage**: Warning at 3.0V, Critical at 2.8V
- **Overcurrent**: Warning at 80A, Critical at 95A

## 📊 System Health Status

Health status levels:
- **healthy**: No faults detected
- **warning**: Minor issues present
- **degraded**: Multiple warnings
- **critical**: Critical faults detected

## 🛠️ Development

### Code Quality

The project uses:
- Type hints throughout
- Comprehensive docstrings
- Error handling
- Logging
- Async/await patterns

### Adding New Sensors

1. Add sensor class to `server/hal/simulator.py`
2. Register in `HardwareSimulator.__init__`
3. Add read method
4. Update MCP tools in `server/main.py`
5. Add tests in `tests/test_simulator.py`

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review test cases for examples

## 🎓 Learn More

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [xAI Grok API](https://x.ai/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

---

**Built with ❤️ using MCP and xAI Grok**
