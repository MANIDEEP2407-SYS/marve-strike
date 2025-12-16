"""
logic_cpu.py
------------
CPU turn logic entry point.

This file exists to keep backward compatibility and provide
a clean import surface for the CPU AI.

Actual greedy logic lives in:
logic_cpu/cpu_controller.py
"""

from logic_cpu.cpu_controller import cpu_turn

__all__ = ["cpu_turn"]
