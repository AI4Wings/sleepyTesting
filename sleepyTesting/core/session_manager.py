"""
Session management interface and implementations for sleepyTesting framework.

This module provides the core session management functionality through:
1. ISessionManager interface defining the contract for session managers
2. InMemorySessionManager as a basic dictionary-based implementation
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ISessionManager(ABC):
    """
    Interface defining the contract for session management
    implementations.
    """

    @abstractmethod
    def start_session(
        self,
        session_id: str
    ) -> None:
        """
        Initialize a new session with the given ID.

        Args:
            session_id: Unique identifier for the session

        Raises:
            ValueError: If session_id already exists
        """
        pass

    @abstractmethod
    def get_data(self, key: str) -> Any:
        """
        Retrieve data stored under the given key in current session.

        Args:
            key: Key to lookup

        Returns:
            The stored value

        Raises:
            KeyError: If key not found
            RuntimeError: If no active session
        """
        pass

    @abstractmethod
    def set_data(
        self,
        key: str,
        value: Any
    ) -> None:
        """
        Store data under the given key in current session.

        Args:
            key: Key to store value under
            value: Value to store

        Raises:
            RuntimeError: If no active session
        """
        pass

    @abstractmethod
    def end_session(self) -> None:
        """
        End the current session and cleanup resources.

        Raises:
            RuntimeError: If no active session
        """
        pass


class InMemorySessionManager(ISessionManager):
    """Basic session manager implementation using in-memory dictionary
    storage."""

    def __init__(self):
        """Initialize the session manager."""
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._current_session: Optional[str] = None

    def start_session(self, session_id: str) -> None:
        """Start a new session. See ISessionManager.start_session."""
        if session_id in self._sessions:
            raise ValueError(f"Session '{session_id}' already exists")

        self._sessions[session_id] = {}
        self._current_session = session_id

    def get_data(self, key: str) -> Any:
        """Get session data. See ISessionManager.get_data."""
        if not self._current_session:
            raise RuntimeError("No active session")

        session_data = self._sessions[self._current_session]
        if key not in session_data:
            raise KeyError(f"Key '{key}' not found in session")

        return session_data[key]

    def set_data(self, key: str, value: Any) -> None:
        """Set session data. See ISessionManager.set_data."""
        if not self._current_session:
            raise RuntimeError("No active session")

        self._sessions[self._current_session][key] = value

    def end_session(self) -> None:
        """End current session. See ISessionManager.end_session."""
        if not self._current_session:
            raise RuntimeError("No active session")

        del self._sessions[self._current_session]
        self._current_session = None
