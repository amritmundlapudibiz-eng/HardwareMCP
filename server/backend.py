"""
Backend Factory

Returns the active hardware backend based on HARDWAREMCP_BACKEND env var.

Current backends:
  simulator — pure Python, no hardware needed (default)

Planned:
  socketcan — Linux SocketCAN for real CAN bus
  serial    — UART/USB serial devices

To add a new backend:
  1. Subclass HardwareBackend in server/hal/your_backend.py
  2. Add an elif branch here
  3. Set HARDWAREMCP_BACKEND=your_backend
"""

from __future__ import annotations

from typing import Optional
from server.hal.base import HardwareBackend


_backend: Optional[HardwareBackend] = None


def get_backend(name: str = "simulator") -> HardwareBackend:
    """
    Return the global backend instance, creating it if needed.

    The name parameter comes from HARDWAREMCP_BACKEND in main().
    Once created, the same instance is reused for the lifetime of
    the server — backends maintain connection state internally.
    """
    global _backend

    if _backend is not None:
        return _backend

    if name == "simulator":
        from server.hal.simulator import SimulatorBackend
        _backend = SimulatorBackend()

    elif name == "socketcan":
        raise NotImplementedError(
            "SocketCAN backend not yet implemented. "
            "See server/hal/base.py to implement it. PRs welcome."
        )

    elif name == "serial":
        raise NotImplementedError(
            "Serial backend not yet implemented. "
            "See server/hal/base.py to implement it. PRs welcome."
        )

    else:
        raise ValueError(
            f"Unknown backend '{name}'. "
            f"Valid options: simulator, socketcan, serial. "
            f"Set via HARDWAREMCP_BACKEND env var."
        )

    return _backend
