"""
Registry for managing external tools in the sleepyTesting framework.

This module provides the ToolRegistry class for registering and managing
tools, as well as the global registry instance that should be used
throughout the framework.

The registry follows a simple key-value pattern where tools are registered
with string names and can be called using those names. Each tool must
implement the BaseTool interface.

Example:
    >>> registry = ToolRegistry()
    >>> registry.register_tool("weather", WeatherTool())
    >>> result = registry.call_tool("weather", {"city": "Beijing"})
"""
from typing import Any, Dict
from .base_tool import BaseTool


class ToolRegistry:
    """
    Registry for managing and executing external tools.

    The registry maintains a collection of tools that can be registered
    and called by name. Each tool must implement the BaseTool interface
    to ensure consistent behavior.
    """

    def __init__(self):
        """Initialize an empty tool registry."""
        self._tools = {}

    def register_tool(self, name: str, tool: BaseTool) -> None:
        """
        Register a new tool with the given name.

        Args:
            name: String identifier for the tool
            tool: Tool instance implementing BaseTool interface

        Raises:
            TypeError: If tool doesn't implement BaseTool interface
            ValueError: If name is already registered
        """
        if not isinstance(tool, BaseTool):
            raise TypeError("Tool must implement BaseTool interface")
        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered")
        self._tools[name] = tool

    def call_tool(self, name: str, params: Dict[str, Any]) -> Any:
        """
        Call a registered tool with the given parameters.

        Args:
            name: Name of the tool to call
            params: Parameters to pass to the tool

        Returns:
            Any: Result from the tool execution

        Raises:
            ValueError: If tool is not found in registry
            Exception: If tool execution fails
        """
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry")

        tool = self._tools[name]
        tool.validate_params(params)
        return tool.execute(params)


# Global registry instance to be used throughout the framework
global_tool_registry = ToolRegistry()
