"""
xAI Grok Agent for HardwareMCP

This module demonstrates how to build an AI agent that connects to the HardwareMCP
server and uses xAI's Grok API (OpenAI-compatible) to intelligently query and
analyze hardware data.

The agent can:
- Query hardware sensors through MCP tools
- Analyze sensor data using Grok's AI capabilities
- Detect anomalies and provide insights
- Generate reports on system health

Usage:
    export XAI_API_KEY="your-api-key-here"
    python agent/gemini_agent.py
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


class HardwareMCPAgent:
    """
    AI Agent that uses xAI Grok to interact with HardwareMCP server

    This agent demonstrates how to:
    1. Connect to an MCP server
    2. Use AI to decide which tools to call
    3. Analyze hardware data intelligently
    4. Provide actionable insights
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the agent with xAI Grok API

        Args:
            api_key: xAI API key (defaults to XAI_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "XAI_API_KEY environment variable must be set or api_key must be provided"
            )

        # Initialize OpenAI client with xAI endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )

        self.conversation_history: List[ChatCompletionMessageParam] = []

    def _add_to_history(self, role: str, content: str) -> None:
        """Add a message to conversation history"""
        if role == "user":
            self.conversation_history.append(
                {"role": "user", "content": content})
        elif role == "assistant":
            self.conversation_history.append(
                {"role": "assistant", "content": content})

    async def query_hardware(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query hardware through MCP tools (simulated for demonstration)

        In a real implementation, this would use the MCP client to call tools
        on the HardwareMCP server. For this example, we simulate the responses.

        Args:
            tool_name: Name of the MCP tool to call
            arguments: Arguments for the tool

        Returns:
            Tool execution result
        """
        # Simulate MCP tool calls
        # In production, this would use the actual MCP client
        print(f"[MCP] Calling tool: {tool_name} with args: {arguments}")

        # Import simulator for demonstration
        from server.hal.simulator import get_simulator
        simulator = get_simulator()

        if tool_name == "read_temperature":
            result = await simulator.read_temperature(arguments["sensor_name"])
        elif tool_name == "read_voltage":
            result = await simulator.read_voltage(arguments["cell_name"])
        elif tool_name == "read_current":
            result = await simulator.read_current(arguments["channel_name"])
        elif tool_name == "read_can_message":
            result = await simulator.read_can_message()
        elif tool_name == "read_gpio":
            result = await simulator.read_gpio(arguments["pin_number"])
        elif tool_name == "read_imu":
            result = await simulator.read_imu()
        elif tool_name == "run_fault_detection":
            result = await simulator.run_fault_detection()
        elif tool_name == "get_system_health":
            result = await simulator.get_system_health()
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

        return result

    def analyze_with_grok(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Use Grok to analyze data or answer questions

        Args:
            prompt: The question or analysis request
            context: Optional context (e.g., sensor data)

        Returns:
            Grok's response
        """
        messages: List[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": (
                    "You are an expert hardware monitoring AI assistant. "
                    "You analyze sensor data from vehicles and industrial equipment, "
                    "detect anomalies, and provide actionable insights. "
                    "You have access to temperature sensors, voltage cells, current channels, "
                    "CAN bus data, GPIO pins, and IMU sensors."
                )
            }
        ]

        # Add conversation history
        messages.extend(self.conversation_history)

        # Add current prompt with context
        if context:
            full_prompt = f"{prompt}\n\nContext:\n{context}"
        else:
            full_prompt = prompt

        messages.append({"role": "user", "content": full_prompt})

        # Call Grok API
        response = self.client.chat.completions.create(
            model="grok-beta",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        assistant_message = response.choices[0].message.content or ""

        # Update conversation history
        self._add_to_history("user", full_prompt)
        self._add_to_history("assistant", assistant_message)

        return assistant_message

    async def check_system_health(self) -> str:
        """
        Check overall system health and provide analysis

        Returns:
            Analysis report from Grok
        """
        print("\n=== Checking System Health ===")

        # Get system health data
        health_data = await self.query_hardware("get_system_health", {})

        # Format data for Grok
        context = json.dumps(health_data, indent=2)

        # Ask Grok to analyze
        prompt = (
            "Analyze this hardware system health data. "
            "Identify any concerns, anomalies, or areas that need attention. "
            "Provide a clear summary of the system status."
        )

        analysis = self.analyze_with_grok(prompt, context)

        return analysis

    async def detect_faults(self) -> str:
        """
        Run fault detection and analyze results

        Returns:
            Fault analysis from Grok
        """
        print("\n=== Running Fault Detection ===")

        # Run fault detection
        fault_data = await self.query_hardware("run_fault_detection", {})

        # Format data for Grok
        context = json.dumps(fault_data, indent=2)

        # Ask Grok to analyze
        prompt = (
            "Analyze these fault detection results. "
            "Explain the severity of each fault, potential causes, "
            "and recommended actions to resolve them."
        )

        analysis = self.analyze_with_grok(prompt, context)

        return analysis

    async def monitor_temperatures(self) -> str:
        """
        Monitor all temperature sensors and analyze

        Returns:
            Temperature analysis from Grok
        """
        print("\n=== Monitoring Temperatures ===")

        # Read all temperature sensors
        sensors = ["engine", "battery", "ambient", "motor"]
        temp_data = {}

        for sensor in sensors:
            data = await self.query_hardware("read_temperature", {"sensor_name": sensor})
            temp_data[sensor] = data

        # Format data for Grok
        context = json.dumps(temp_data, indent=2)

        # Ask Grok to analyze
        prompt = (
            "Analyze these temperature readings from a vehicle. "
            "Are any temperatures concerning? "
            "What do these readings tell us about the vehicle's operating condition?"
        )

        analysis = self.analyze_with_grok(prompt, context)

        return analysis

    async def check_battery_health(self) -> str:
        """
        Check battery cell voltages and analyze health

        Returns:
            Battery analysis from Grok
        """
        print("\n=== Checking Battery Health ===")

        # Read all voltage cells
        cells = ["cell_1", "cell_2", "cell_3", "cell_4"]
        voltage_data = {}

        for cell in cells:
            data = await self.query_hardware("read_voltage", {"cell_name": cell})
            voltage_data[cell] = data

        # Format data for Grok
        context = json.dumps(voltage_data, indent=2)

        # Ask Grok to analyze
        prompt = (
            "Analyze these battery cell voltages. "
            "Is the battery balanced? Are any cells showing signs of degradation? "
            "What is the overall battery health status?"
        )

        analysis = self.analyze_with_grok(prompt, context)

        return analysis

    async def analyze_can_messages(self, count: int = 5) -> str:
        """
        Capture and analyze CAN bus messages

        Args:
            count: Number of messages to capture

        Returns:
            CAN message analysis from Grok
        """
        print(f"\n=== Analyzing {count} CAN Messages ===")

        # Capture multiple CAN messages
        messages = []
        for _ in range(count):
            data = await self.query_hardware("read_can_message", {})
            messages.append(data)
            await asyncio.sleep(0.1)  # Small delay between reads

        # Format data for Grok
        context = json.dumps(messages, indent=2)

        # Ask Grok to analyze
        prompt = (
            "Analyze these CAN bus messages from a Cascadia CM200DZ motor controller. "
            "What information can you extract about the motor's operation? "
            "Are there any patterns or anomalies?"
        )

        analysis = self.analyze_with_grok(prompt, context)

        return analysis

    async def run_comprehensive_analysis(self) -> None:
        """
        Run a comprehensive analysis of all hardware systems
        """
        print("\n" + "="*60)
        print("HardwareMCP AI Agent - Comprehensive System Analysis")
        print("Powered by xAI Grok")
        print("="*60)

        # 1. System Health Check
        print("\n[1/5] System Health Check...")
        health_analysis = await self.check_system_health()
        print(f"\n{health_analysis}\n")

        # 2. Fault Detection
        print("\n[2/5] Fault Detection...")
        fault_analysis = await self.detect_faults()
        print(f"\n{fault_analysis}\n")

        # 3. Temperature Monitoring
        print("\n[3/5] Temperature Monitoring...")
        temp_analysis = await self.monitor_temperatures()
        print(f"\n{temp_analysis}\n")

        # 4. Battery Health
        print("\n[4/5] Battery Health Check...")
        battery_analysis = await self.check_battery_health()
        print(f"\n{battery_analysis}\n")

        # 5. CAN Bus Analysis
        print("\n[5/5] CAN Bus Analysis...")
        can_analysis = await self.analyze_can_messages()
        print(f"\n{can_analysis}\n")

        # Final Summary
        print("\n" + "="*60)
        print("Analysis Complete")
        print("="*60)

        # Ask Grok for overall summary
        summary_prompt = (
            "Based on all the analyses we've done (system health, faults, "
            "temperatures, battery, and CAN messages), provide a brief executive "
            "summary of the vehicle's overall condition and any priority actions needed."
        )

        summary = self.analyze_with_grok(summary_prompt)
        print(f"\nExecutive Summary:\n{summary}\n")


async def main():
    """
    Main entry point for the agent demonstration
    """
    try:
        # Initialize agent
        agent = HardwareMCPAgent()

        # Run comprehensive analysis
        await agent.run_comprehensive_analysis()

    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set your XAI_API_KEY environment variable:")
        print("  export XAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    """
    Run the agent when executed directly

    Usage:
        export XAI_API_KEY="your-api-key-here"
        python agent/gemini_agent.py
    """
    asyncio.run(main())

# Made with Bob
