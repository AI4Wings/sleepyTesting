"""
Tools package for sleepyTesting framework.

This package provides the infrastructure for integrating external tools
into the UI automation workflow. It includes:

- A base tool interface that all tools must implement
- A registry for managing and discovering tools
- Built-in tools for common operations
"""

from .weather_tool import WeatherTool
from .tool_registry import global_tool_registry

# Register built-in tools
global_tool_registry.register_tool("weather", WeatherTool())
