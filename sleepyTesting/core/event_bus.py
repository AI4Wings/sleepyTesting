"""
Event bus system for inter-module communication in sleepyTesting framework.

This module provides a publish/subscribe event system that enables decoupled
communication between different components of the framework.
"""
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List
import threading
from typing import TypeVar, Generic

T = TypeVar('T')


class Event(Generic[T]):
    """Generic event class to type-safe event payloads."""

    def __init__(self, event_type: str, payload: T):
        """
        Initialize an event.

        Args:
            event_type: The type/name of the event
            payload: The event data
        """
        self.event_type = event_type
        self.payload = payload


class IEventBus(ABC):
    """Interface defining the contract for event bus implementations."""

    @abstractmethod
    def subscribe(
        self,
        event_type: str,
        callback: Callable[[Any], None]
    ) -> None:
        """
        Subscribe to events of a specific type.

        Args:
            event_type: The type of events to subscribe to
            callback: Function to call when event occurs
        """
        pass

    @abstractmethod
    def unsubscribe(
        self,
        event_type: str,
        callback: Callable[[Any], None]
    ) -> None:
        """
        Unsubscribe from events of a specific type.

        Args:
            event_type: The type of events to unsubscribe from
            callback: The callback function to remove

        Raises:
            ValueError: If callback is not subscribed to event_type
        """
        pass

    @abstractmethod
    def publish(self, event: Event[Any]) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: The event to publish
        """
        pass


class EventBus(IEventBus):
    """Thread-safe implementation of the event bus interface."""

    def __init__(self):
        """Initialize the event bus."""
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = {}
        self._lock = threading.Lock()

    def subscribe(
        self,
        event_type: str,
        callback: Callable[[Any], None]
    ) -> None:
        """Subscribe to events. See IEventBus.subscribe."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)

    def unsubscribe(
        self,
        event_type: str,
        callback: Callable[[Any], None]
    ) -> None:
        """Unsubscribe from events. See IEventBus.unsubscribe."""
        with self._lock:
            if event_type not in self._subscribers:
                msg = f"No subscribers for event type: {event_type}"
                raise ValueError(msg)

            try:
                self._subscribers[event_type].remove(callback)
                if not self._subscribers[event_type]:
                    del self._subscribers[event_type]
            except ValueError:
                raise ValueError(
                    "Callback not subscribed to event type: "
                    f"{event_type}"
                )

    def publish(self, event: Event[Any]) -> None:
        """Publish an event. See IEventBus.publish."""
        with self._lock:
            handlers = self._subscribers.get(event.event_type, []).copy()

        # Execute handlers outside the lock
        for handler in handlers:
            try:
                handler(event.payload)
            except Exception as e:
                # In a production system, we'd want to log this
                print(f"Error in event handler: {e}")


# Common event types used in the framework
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentEventPayload:
    """Payload for agent-related events."""
    agent_id: str
    timestamp: datetime = datetime.now()
    message: str = ""
    error: Exception = None


class EventTypes:
    """Constants for common event types used in the framework."""

    # Task-related events
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    
    # Assertion events
    ASSERTION_FAILED = "assertion_failed"
    ASSERTION_PASSED = "assertion_passed"
    
    # Session events
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    
    # Agent lifecycle events
    AGENT_INITIALIZED = "agent_initialized"
    AGENT_READY = "agent_ready"
    AGENT_BUSY = "agent_busy"
    AGENT_ERROR = "agent_error"
    AGENT_RECOVERED = "agent_recovered"
    AGENT_SHUTDOWN = "agent_shutdown"
    
    # Health monitoring events
    HEALTH_CHECK = "health_check"
    HEALTH_CHECK_FAILED = "health_check_failed"
    HEALTH_CHECK_PASSED = "health_check_passed"
    
    # Memory events
    MEMORY_UPDATED = "memory_updated"
    MEMORY_CLEARED = "memory_cleared"
