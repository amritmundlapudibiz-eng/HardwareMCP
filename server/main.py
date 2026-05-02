"""
HardwareMCP Server

This is the main MCP (Model Context Protocol) server that exposes hardware
monitoring and control capabilities through a standardized interface. It uses
the stdio transport for communication and provides 8 tools for interacting
with hardware components.

Tools:
1. read_temperature - Read temperature from sensors
2. read_voltage - Read voltage from battery cells
3. read_current - Read current from channels
4. read_can_message - Read CAN bus messages
5. read_gpio - Read GPIO pin states
6. read_imu - Read IMU (accelerometer/gyroscope) data
7. run_fault_detection - Run comprehensive fault detection
8. get_system_health - Get overall system health status
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from server.hal.simulator import get_simulator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize the MCP server
app = Server("hardwaremcp")


# Tool definitions
TOOLS = [
    Tool(
        name="read_temperature",
        description=(
            "Read temperature from a specific sensor. "
            "Available sensors: engine, battery, ambient, motor. "
            "Returns temperature in Celsius and Fahrenheit with timestamp."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "sensor_name": {
                    "type": "string",
                    "description": "Name of the temperature sensor",
                    "enum": ["engine", "battery", "ambient", "motor"]
                }
            },
            "required": ["sensor_name"]
        }
    ),
    Tool(
        name="read_voltage",
        description=(
            "Read voltage from a specific battery cell. "
            "Available cells: cell_1, cell_2, cell_3, cell_4. "
            "Returns voltage in volts with timestamp."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "cell_name": {
                    "type": "string",
                    "description": "Name of the voltage cell",
                    "enum": ["cell_1", "cell_2", "cell_3", "cell_4"]
                }
            },
            "required": ["cell_name"]
        }
    ),
    Tool(
        name="read_current",
        description=(
            "Read current from a specific channel. "
            "Available channels: motor, bms, aux. "
            "Returns current in amperes with timestamp."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "channel_name": {
                    "type": "string",
                    "description": "Name of the current channel",
                    "enum": ["motor", "bms", "aux"]
                }
            },
            "required": ["channel_name"]
        }
    ),
    Tool(
        name="read_can_message",
        description=(
            "Read a CAN bus message from the Cascadia CM200DZ inverter. "
            "Returns CAN message with ID, data bytes, and timestamp. "
            "Simulates real motor controller communication."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="read_gpio",
        description=(
            "Read the state of a GPIO pin. "
            "Available pins: 0-5 (pins 0,1,4 are inputs; pins 2,3,5 are outputs). "
            "Returns pin state (true/false) and mode."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "pin_number": {
                    "type": "integer",
                    "description": "GPIO pin number (0-5)",
                    "minimum": 0,
                    "maximum": 5
                }
            },
            "required": ["pin_number"]
        }
    ),
    Tool(
        name="read_imu",
        description=(
            "Read IMU (Inertial Measurement Unit) data including accelerometer "
            "and gyroscope readings. Returns 3-axis acceleration (m/s²) and "
            "3-axis rotation rates (rad/s) with timestamp."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="run_fault_detection",
        description=(
            "Run comprehensive fault detection across all sensors. "
            "Checks for overvoltage, undervoltage, overtemperature, and overcurrent "
            "conditions. Returns list of detected faults with severity levels "
            "(warning/critical) and affected sensors."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_system_health",
        description=(
            "Get overall system health status including all sensor readings, "
            "average metrics, fault summary, and uptime. Provides a comprehensive "
            "view of the entire hardware system state."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools

    Returns:
        List of Tool objects describing available hardware operations
    """
    logger.info("Listing available tools")
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """
    Handle tool calls from MCP clients

    Args:
        name: Name of the tool to call
        arguments: Dictionary of arguments for the tool

    Returns:
        List of TextContent with the tool result

    Raises:
        ValueError: If tool name is unknown or arguments are invalid
    """
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    simulator = get_simulator()

    try:
        if name == "read_temperature":
            sensor_name = arguments.get("sensor_name")
            if not sensor_name:
                raise ValueError("sensor_name is required")
            result = await simulator.read_temperature(sensor_name)

        elif name == "read_voltage":
            cell_name = arguments.get("cell_name")
            if not cell_name:
                raise ValueError("cell_name is required")
            result = await simulator.read_voltage(cell_name)

        elif name == "read_current":
            channel_name = arguments.get("channel_name")
            if not channel_name:
                raise ValueError("channel_name is required")
            result = await simulator.read_current(channel_name)

        elif name == "read_can_message":
            result = await simulator.read_can_message()

        elif name == "read_gpio":
            pin_number = arguments.get("pin_number")
            if pin_number is None:
                raise ValueError("pin_number is required")
            result = await simulator.read_gpio(pin_number)

        elif name == "read_imu":
            result = await simulator.read_imu()

        elif name == "run_fault_detection":
            result = await simulator.run_fault_detection()

        elif name == "get_system_health":
            result = await simulator.get_system_health()

        else:
            raise ValueError(f"Unknown tool: {name}")

        # Format result as JSON string
        result_text = json.dumps(result, indent=2)

        logger.info(f"Tool {name} executed successfully")
        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        error_msg = f"Error executing tool {name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type="text", text=json.dumps({"error": error_msg}))]


async def main():
    """
    Main entry point for the MCP server

    Starts the server using stdio transport for communication with MCP clients.
    The server will run until interrupted or the client disconnects.
    """
    logger.info("Starting HardwareMCP server...")

    try:
        # Run the server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server initialized with stdio transport")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
    finally:
        logger.info("HardwareMCP server stopped")


if __name__ == "__main__":
    """
    Run the server when executed directly

    Usage:
        python -m server.main
    """
    asyncio.run(main())

# Made with Bob
