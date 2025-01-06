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
    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: The type of events to subscribe to
            callback: Function to call when event occurs
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
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
    
    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Subscribe to events. See IEventBus.subscribe."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Unsubscribe from events. See IEventBus.unsubscribe."""
        with self._lock:
            if event_type not in self._subscribers:
                raise ValueError(f"No subscribers for event type: {event_type}")
                
            try:
                self._subscribers[event_type].remove(callback)
                if not self._subscribers[event_type]:
                    del self._subscribers[event_type]
            except ValueError:
                raise ValueError(
                    f"Callback not subscribed to event type: {event_type}"
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
class EventTypes:
    """Constants for common event types used in the framework."""
    
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    ASSERTION_FAILED = "assertion_failed"
    ASSERTION_PASSED = "assertion_passed"
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
