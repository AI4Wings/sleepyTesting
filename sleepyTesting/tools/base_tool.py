"""
Base interface for external tools in the sleepyTesting framework.

All tools must inherit from BaseTool and implement its abstract methods
to ensure consistent behavior across the framework.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validate parameters required by this tool.

        Args:
            params: Dictionary of parameters to validate

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Execute the tool logic, returning any result needed
        by other automation steps.

        Args:
            params: Dictionary of parameters for tool execution

        Returns:
            Any: Result of the tool execution that can be used
                 in subsequent automation steps

        Raises:
            Exception: If tool execution fails
        """
        pass
