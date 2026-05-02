# HardwareMCP API Reference

## Overview

Complete API reference for HardwareMCP MCP tools, resources, and configuration options.

## MCP Tools

### High-Level Tools

#### read_sensor
Read data from a sensor device.

**Parameters:**
- `protocol` (string, required): Protocol name (gpio, i2c, spi, uart, can, mqtt, modbus)
- `device_id` (string, required): Device identifier from configuration
- `parameters` (object, optional): Protocol-specific parameters

**Returns:**
```json
{
  "device_id": "temp_sensor_1",
  "protocol": "i2c",
  "value": 23.5,
  "unit": "celsius",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example:**
```json
{
  "protocol": "i2c",
  "device_id": "temp_sensor_1"
}
```

#### write_actuator
Control an actuator device.

**Parameters:**
- `protocol` (string, required): Protocol name
- `device_id` (string, required): Device identifier
- `value` (any, required): Value to write (type depends on device)
- `parameters` (object, optional): Protocol-specific parameters

**Returns:**
```json
{
  "device_id": "relay_1",
  "protocol": "gpio",
  "status": "success",
  "value": "on",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example:**
```json
{
  "protocol": "gpio",
  "device_id": "relay_1",
  "value": "on"
}
```

#### send_message
Send a message via a communication protocol.

**Parameters:**
- `protocol` (string, required): Protocol name (can, mqtt, uart)
- `destination` (string, required): Destination address/topic
- `data` (string|bytes, required): Message data
- `parameters` (object, optional): Protocol-specific parameters

**Returns:**
```json
{
  "protocol": "mqtt",
  "destination": "sensors/temperature",
  "status": "published",
  "message_id": "msg_123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example:**
```json
{
  "protocol": "mqtt",
  "destination": "sensors/temperature",
  "data": "{\"temp\": 23.5}"
}
```

#### configure_device
Configure a device's settings.

**Parameters:**
- `protocol` (string, required): Protocol name
- `device_id` (string, required): Device identifier
- `config` (object, required): Configuration parameters

**Returns:**
```json
{
  "device_id": "uart_1",
  "protocol": "uart",
  "status": "configured",
  "config": {
    "baudrate": 115200,
    "parity": "none"
  }
}
```

**Example:**
```json
{
  "protocol": "uart",
  "device_id": "uart_1",
  "config": {
    "baudrate": 115200,
    "parity": "none"
  }
}
```

#### scan_bus
Discover devices on a bus.

**Parameters:**
- `protocol` (string, required): Protocol name (i2c, can)
- `parameters` (object, optional): Scan parameters

**Returns:**
```json
{
  "protocol": "i2c",
  "devices": [
    {"address": "0x48", "type": "unknown"},
    {"address": "0x76", "type": "bme280"}
  ],
  "scan_time": "2024-01-15T10:30:00Z"
}
```

**Example:**
```json
{
  "protocol": "i2c"
}
```

### GPIO Tools

#### gpio_read
Read the state of a GPIO pin.

**Parameters:**
- `pin` (integer, required): Pin number (0-40)

**Returns:**
```json
{
  "pin": 17,
  "value": 1,
  "mode": "input",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### gpio_write
Write a value to a GPIO pin.

**Parameters:**
- `pin` (integer, required): Pin number (0-40)
- `value` (integer|string, required): 0/1 or "low"/"high"

**Returns:**
```json
{
  "pin": 17,
  "value": 1,
  "status": "success"
}
```

#### gpio_setup
Configure a GPIO pin.

**Parameters:**
- `pin` (integer, required): Pin number
- `mode` (string, required): "input", "output", or "pwm"
- `pull` (string, optional): "up", "down", or "none"
- `initial` (integer, optional): Initial value for output pins

**Returns:**
```json
{
  "pin": 17,
  "mode": "output",
  "pull": "none",
  "status": "configured"
}
```

#### gpio_pwm
Control PWM on a pin.

**Parameters:**
- `pin` (integer, required): Pin number
- `duty_cycle` (number, required): Duty cycle (0-100)
- `frequency` (number, optional): PWM frequency in Hz

**Returns:**
```json
{
  "pin": 18,
  "duty_cycle": 50,
  "frequency": 1000,
  "status": "success"
}
```

### I2C Tools

#### i2c_read_register
Read from an I2C device register.

**Parameters:**
- `address` (integer, required): I2C device address (0x00-0x7F)
- `register` (integer, required): Register address
- `length` (integer, optional): Number of bytes to read (default: 1)

**Returns:**
```json
{
  "address": "0x48",
  "register": "0x00",
  "data": [0x12, 0x34],
  "length": 2
}
```

#### i2c_write_register
Write to an I2C device register.

**Parameters:**
- `address` (integer, required): I2C device address
- `register` (integer, required): Register address
- `data` (array|integer, required): Data to write

**Returns:**
```json
{
  "address": "0x48",
  "register": "0x01",
  "bytes_written": 2,
  "status": "success"
}
```

#### i2c_scan
Scan I2C bus for devices.

**Parameters:**
- `bus` (integer, optional): Bus number (default: 1)

**Returns:**
```json
{
  "bus": 1,
  "devices": ["0x48", "0x76"],
  "count": 2
}
```

### SPI Tools

#### spi_transfer
Perform SPI transfer.

**Parameters:**
- `data` (array, required): Data to send
- `cs` (integer, optional): Chip select pin
- `speed` (integer, optional): Transfer speed in Hz

**Returns:**
```json
{
  "sent": [0x01, 0x02, 0x03],
  "received": [0x00, 0xAB, 0xCD],
  "length": 3
}
```

#### spi_read
Read data from SPI device.

**Parameters:**
- `length` (integer, required): Number of bytes to read
- `cs` (integer, optional): Chip select pin

**Returns:**
```json
{
  "data": [0x12, 0x34, 0x56],
  "length": 3
}
```

#### spi_write
Write data to SPI device.

**Parameters:**
- `data` (array, required): Data to write
- `cs` (integer, optional): Chip select pin

**Returns:**
```json
{
  "bytes_written": 3,
  "status": "success"
}
```

### UART Tools

#### uart_read
Read data from UART.

**Parameters:**
- `port` (string, required): Serial port path
- `length` (integer, optional): Number of bytes to read
- `timeout` (number, optional): Read timeout in seconds

**Returns:**
```json
{
  "port": "/dev/ttyUSB0",
  "data": "Hello World",
  "bytes_read": 11
}
```

#### uart_write
Write data to UART.

**Parameters:**
- `port` (string, required): Serial port path
- `data` (string|array, required): Data to write

**Returns:**
```json
{
  "port": "/dev/ttyUSB0",
  "bytes_written": 11,
  "status": "success"
}
```

#### uart_configure
Configure UART port.

**Parameters:**
- `port` (string, required): Serial port path
- `baudrate` (integer, required): Baud rate
- `parity` (string, optional): "none", "even", "odd"
- `stopbits` (number, optional): 1 or 2
- `bytesize` (integer, optional): 5, 6, 7, or 8

**Returns:**
```json
{
  "port": "/dev/ttyUSB0",
  "baudrate": 115200,
  "parity": "none",
  "stopbits": 1,
  "bytesize": 8,
  "status": "configured"
}
```

### CAN Tools

#### can_send_frame
Send a CAN frame.

**Parameters:**
- `id` (integer, required): CAN ID
- `data` (array, required): Data bytes (0-8 bytes)
- `extended` (boolean, optional): Use extended ID
- `interface` (string, optional): CAN interface name

**Returns:**
```json
{
  "id": "0x123",
  "data": [0x01, 0x02, 0x03],
  "extended": false,
  "status": "sent"
}
```

#### can_receive_frame
Receive a CAN frame.

**Parameters:**
- `timeout` (number, optional): Receive timeout in seconds
- `interface` (string, optional): CAN interface name

**Returns:**
```json
{
  "id": "0x456",
  "data": [0xAB, 0xCD],
  "extended": false,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### can_set_filter
Set CAN receive filter.

**Parameters:**
- `filters` (array, required): Array of filter objects
- `interface` (string, optional): CAN interface name

**Returns:**
```json
{
  "filters": [
    {"id": "0x100", "mask": "0x7FF"}
  ],
  "status": "configured"
}
```

### MQTT Tools

#### mqtt_publish
Publish MQTT message.

**Parameters:**
- `topic` (string, required): Topic to publish to
- `message` (string, required): Message payload
- `qos` (integer, optional): QoS level (0, 1, 2)
- `retain` (boolean, optional): Retain message

**Returns:**
```json
{
  "topic": "sensors/temperature",
  "message_id": "msg_123",
  "qos": 1,
  "status": "published"
}
```

#### mqtt_subscribe
Subscribe to MQTT topic.

**Parameters:**
- `topic` (string, required): Topic pattern to subscribe to
- `qos` (integer, optional): QoS level

**Returns:**
```json
{
  "topic": "sensors/#",
  "qos": 1,
  "status": "subscribed"
}
```

#### mqtt_unsubscribe
Unsubscribe from MQTT topic.

**Parameters:**
- `topic` (string, required): Topic to unsubscribe from

**Returns:**
```json
{
  "topic": "sensors/#",
  "status": "unsubscribed"
}
```

### Modbus Tools

#### modbus_read_coils
Read Modbus coils.

**Parameters:**
- `address` (integer, required): Starting address
- `count` (integer, required): Number of coils to read
- `slave_id` (integer, optional): Slave device ID

**Returns:**
```json
{
  "address": 0,
  "count": 8,
  "values": [true, false, true, false, true, false, true, false]
}
```

#### modbus_write_coil
Write Modbus coil.

**Parameters:**
- `address` (integer, required): Coil address
- `value` (boolean, required): Coil value
- `slave_id` (integer, optional): Slave device ID

**Returns:**
```json
{
  "address": 0,
  "value": true,
  "status": "success"
}
```

#### modbus_read_registers
Read Modbus holding registers.

**Parameters:**
- `address` (integer, required): Starting address
- `count` (integer, required): Number of registers to read
- `slave_id` (integer, optional): Slave device ID

**Returns:**
```json
{
  "address": 0,
  "count": 4,
  "values": [1234, 5678, 9012, 3456]
}
```

#### modbus_write_register
Write Modbus holding register.

**Parameters:**
- `address` (integer, required): Register address
- `value` (integer, required): Register value
- `slave_id` (integer, optional): Slave device ID

**Returns:**
```json
{
  "address": 0,
  "value": 1234,
  "status": "success"
}
```

## MCP Resources

### hardware://gpio/pins
Stream of GPIO pin states.

**Content Type:** `application/json`

**Format:**
```json
{
  "pins": [
    {"pin": 17, "mode": "output", "value": 1},
    {"pin": 27, "mode": "input", "value": 0, "pull": "up"}
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### hardware://i2c/devices
List of I2C devices.

**Content Type:** `application/json`

**Format:**
```json
{
  "bus": 1,
  "devices": [
    {
      "address": "0x48",
      "type": "temperature_sensor",
      "name": "temp_sensor_1",
      "status": "online"
    }
  ]
}
```

### hardware://can/frames
Stream of CAN bus frames.

**Content Type:** `application/json`

**Format:**
```json
{
  "id": "0x123",
  "data": [0x01, 0x02, 0x03],
  "extended": false,
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

### hardware://mqtt/messages/{topic}
Stream of MQTT messages for a topic.

**Content Type:** `application/json`

**Format:**
```json
{
  "topic": "sensors/temperature",
  "message": "{\"temp\": 23.5}",
  "qos": 1,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### hardware://logs
System logs and events.

**Content Type:** `text/plain`

**Format:**
```
[2024-01-15T10:30:00Z] INFO: GPIO pin 17 set to HIGH
[2024-01-15T10:30:01Z] DEBUG: I2C read from 0x48: [0x12, 0x34]
[2024-01-15T10:30:02Z] ERROR: CAN frame send failed: Bus off
```

## Configuration Schema

### Hardware Configuration

```yaml
hardware:
  # Operation mode: auto, real, simulator
  mode: auto
  
  # Platform: raspberry_pi, esp32, linux, windows, macos
  platform: raspberry_pi
  
  # GPIO Configuration
  gpio:
    enabled: true
    pins:
      - pin: 17
        mode: output  # input, output, pwm
        initial: low  # low, high (for output)
        pull: none    # none, up, down (for input)
      - pin: 27
        mode: input
        pull: up
  
  # I2C Configuration
  i2c:
    enabled: true
    bus: 1
    devices:
      - address: 0x48
        type: temperature_sensor
        name: temp_sensor_1
        config:
          resolution: 12
  
  # SPI Configuration
  spi:
    enabled: true
    bus: 0
    device: 0
    max_speed: 1000000
    mode: 0
  
  # UART Configuration
  uart:
    enabled: true
    port: /dev/ttyUSB0
    baudrate: 9600
    parity: none
    stopbits: 1
    bytesize: 8
  
  # CAN Configuration
  can:
    enabled: true
    interface: can0
    bitrate: 500000
    filters:
      - id: 0x100
        mask: 0x7FF
  
  # MQTT Configuration
  mqtt:
    enabled: true
    broker: localhost
    port: 1883
    client_id: hardwaremcp
    username: null
    password: null
    topics:
      - sensors/#
  
  # Modbus Configuration
  modbus:
    enabled: true
    mode: rtu  # rtu, tcp
    port: /dev/ttyUSB1
    baudrate: 9600
    slave_id: 1
```

### Logging Configuration

```yaml
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: json  # json, text
  output: file  # console, file, both
  file:
    path: /var/log/hardwaremcp/server.log
    max_size: 10485760  # 10MB
    backup_count: 5
  protocols:
    gpio: DEBUG
    i2c: INFO
    spi: INFO
```

### Dashboard Configuration

```yaml
dashboard:
  enabled: true
  host: 0.0.0.0
  port: 8000
  cors_origins:
    - http://localhost:5173
  websocket:
    ping_interval: 30
    max_connections: 100
```

## Error Codes

### General Errors
- `INVALID_PARAMETER`: Invalid parameter value
- `MISSING_PARAMETER`: Required parameter missing
- `CONFIGURATION_ERROR`: Configuration error
- `PERMISSION_DENIED`: Insufficient permissions

### Hardware Errors
- `HARDWARE_NOT_FOUND`: Hardware device not found
- `HARDWARE_BUSY`: Hardware device busy
- `HARDWARE_ERROR`: Hardware operation failed
- `COMMUNICATION_ERROR`: Communication error

### Protocol Errors
- `PROTOCOL_NOT_SUPPORTED`: Protocol not supported
- `PROTOCOL_ERROR`: Protocol-specific error
- `TIMEOUT`: Operation timeout
- `INVALID_ADDRESS`: Invalid device address

### Example Error Response
```json
{
  "error": {
    "code": "HARDWARE_NOT_FOUND",
    "message": "I2C device at address 0x48 not responding",
    "protocol": "i2c",
    "device": "0x48",
    "suggestion": "Check device connection or enable simulator mode"
  }
}
```

## Rate Limits

### Default Limits
- GPIO operations: 1000/second
- I2C operations: 100/second
- SPI operations: 100/second
- UART operations: 100/second
- CAN operations: 1000/second
- MQTT operations: 100/second
- Modbus operations: 10/second

### Configuring Rate Limits
```yaml
rate_limits:
  gpio: 1000
  i2c: 100
  spi: 100
  uart: 100
  can: 1000
  mqtt: 100
  modbus: 10
```

## Versioning

### API Version
Current version: `1.0.0`

### Version Header
Include in requests:
```
X-API-Version: 1.0.0
```

### Compatibility
- Major version changes: Breaking changes
- Minor version changes: New features, backward compatible
- Patch version changes: Bug fixes, backward compatible

## Best Practices

### 1. Error Handling
Always check for errors in responses:
```python
result = await session.call_tool("gpio_read", {"pin": 17})
if result.isError:
    print(f"Error: {result.content[0].text}")
else:
    print(f"Value: {result.content[0].text}")
```

### 2. Resource Management
Use context managers for connections:
```python
async with hardware_session() as session:
    # Use session
    pass
# Automatically cleaned up
```

### 3. Batch Operations
Group related operations:
```python
# Instead of multiple calls
for pin in [17, 27, 22]:
    await gpio_read(pin)

# Use batch operation
await gpio_read_multiple([17, 27, 22])
```

### 4. Caching
Cache static data:
```python
# Cache device list
devices = await list_devices()
# Reuse for multiple operations
```

### 5. Timeouts
Always set appropriate timeouts:
```python
result = await session.call_tool(
    "uart_read",
    {"port": "/dev/ttyUSB0", "timeout": 5.0}
)