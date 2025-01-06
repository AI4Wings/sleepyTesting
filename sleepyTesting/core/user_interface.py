"""
User interface abstraction for the sleepyTesting framework.

This module provides the interface and implementations for user interaction,
allowing the framework to communicate with users in a consistent way across
different environments (console, GUI, headless, etc.).
"""
from abc import ABC, abstractmethod
import sys
from typing import Optional


class IUserInterface(ABC):
    """Interface defining the contract for user interaction."""
    
    @abstractmethod
    def prompt(self, message: str) -> str:
        """
        Prompt the user for input with a message.
        
        Args:
            message: The prompt message to display
            
        Returns:
            The user's response as a string
        """
        pass
    
    @abstractmethod
    def inform(self, message: str) -> None:
        """
        Display an informational message to the user.
        
        Args:
            message: The message to display
        """
        pass
    
    @abstractmethod
    def warn(self, message: str) -> None:
        """
        Display a warning message to the user.
        
        Args:
            message: The warning message to display
        """
        pass
    
    @abstractmethod
    def error(self, message: str) -> None:
        """
        Display an error message to the user.
        
        Args:
            message: The error message to display
        """
        pass


class ConsoleUserInterface(IUserInterface):
    """Console-based implementation of the user interface."""
    
    def prompt(self, message: str) -> str:
        """Prompt user via console. See IUserInterface.prompt."""
        print(f"\n{message}", file=sys.stderr)
        return input("> ").strip()
    
    def inform(self, message: str) -> None:
        """Display info message. See IUserInterface.inform."""
        print(f"\nINFO: {message}", file=sys.stderr)
    
    def warn(self, message: str) -> None:
        """Display warning message. See IUserInterface.warn."""
        print(f"\nWARNING: {message}", file=sys.stderr)
    
    def error(self, message: str) -> None:
        """Display error message. See IUserInterface.error."""
        print(f"\nERROR: {message}", file=sys.stderr)


class NoOpUserInterface(IUserInterface):
    """No-op implementation for headless/testing environments."""
    
    def prompt(self, message: str) -> str:
        """Return empty string. See IUserInterface.prompt."""
        return ""
    
    def inform(self, message: str) -> None:
        """Do nothing. See IUserInterface.inform."""
        pass
    
    def warn(self, message: str) -> None:
        """Do nothing. See IUserInterface.warn."""
        pass
    
    def error(self, message: str) -> None:
        """Do nothing. See IUserInterface.error."""
        pass
