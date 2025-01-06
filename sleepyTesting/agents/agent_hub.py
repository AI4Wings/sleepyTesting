"""
Agent Hub for coordinating multiple agents in the sleepyTesting framework.

This module provides centralized management of all agents, handling their
initialization, coordination, and event subscriptions. It serves as the main
orchestrator for the multi-agent system.
"""
from typing import Dict, Any, Optional

from .controller import ControllerAgent
from .decomposer import TaskDecomposer
from .supervisor import SupervisorAgent
from .memory import MemoryAgent
from ..core.event_bus import IEventBus
from ..core.session_manager import ISessionManager
from ..core.llm_provider import ILLMProvider
from ..core.user_interface import IUserInterface


class AgentHub:
    """
    Centralized hub for managing and coordinating all agents in the system.
    
    This class initializes and manages references to all agents, subscribes to
    relevant event bus topics, and coordinates the overall flow of the system.
    """
    
    def __init__(
        self,
        event_bus: IEventBus,
        session_manager: ISessionManager,
        llm_provider: ILLMProvider,
        user_interface: IUserInterface,
    ):
        """
        Initialize the agent hub with required dependencies.
        
        Args:
            event_bus: Event bus for inter-agent communication
            session_manager: Session management service
            llm_provider: LLM service provider
            user_interface: User interaction interface
        """
        self.event_bus = event_bus
        self.session_manager = session_manager
        self.user_interface = user_interface
        
        # Initialize agents
        self.decomposer = TaskDecomposer(llm_provider)
        self.supervisor = SupervisorAgent()
        self.memory = MemoryAgent()
        self.controller = ControllerAgent(
            decomposer=self.decomposer,
            supervisor=self.supervisor,
            memory=self.memory,
        )
        
        # Subscribe to events
        self._setup_event_subscriptions()
    
    def _setup_event_subscriptions(self) -> None:
        """Set up event subscriptions for all managed agents."""
        # Core workflow events
        self.event_bus.subscribe("TASK_STARTED", self._on_task_started)
        self.event_bus.subscribe("TASK_COMPLETED", self._on_task_completed)
        self.event_bus.subscribe("STEP_EXECUTED", self._on_step_executed)
        self.event_bus.subscribe("ERROR_OCCURRED", self._on_error)
        
        # Memory-related events
        self.event_bus.subscribe("MEMORY_UPDATED", self._on_memory_updated)
    
    def _on_task_started(self, payload: Dict[str, Any]) -> None:
        """Handle task start event."""
        session_id = payload.get("session_id")
        task_id = payload.get("task_id")
        self.user_interface.inform(f"Starting task {task_id} in session {session_id}")
    
    def _on_task_completed(self, payload: Dict[str, Any]) -> None:
        """Handle task completion event."""
        task_id = payload.get("task_id")
        success = payload.get("success", False)
        if success:
            self.user_interface.inform(f"Task {task_id} completed successfully")
        else:
            self.user_interface.warn(f"Task {task_id} completed with issues")
    
    def _on_step_executed(self, payload: Dict[str, Any]) -> None:
        """Handle step execution completion event."""
        step_id = payload.get("step_id")
        result = payload.get("result", {})
        
        # Update memory with step result
        self.memory.store_step_result(step_id, result)
        
        # Notify supervisor for validation
        self.supervisor.validate_step_result(step_id, result)
    
    def _on_error(self, payload: Dict[str, Any]) -> None:
        """Handle error events from any component."""
        error_msg = payload.get("message", "Unknown error occurred")
        source = payload.get("source", "unknown")
        self.user_interface.error(f"Error in {source}: {error_msg}")
    
    def _on_memory_updated(self, payload: Dict[str, Any]) -> None:
        """Handle memory update events."""
        memory_id = payload.get("memory_id")
        self.user_interface.inform(f"Memory updated: {memory_id}")
    
    async def execute_task(self, task_description: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task using the coordinated agent system.
        
        Args:
            task_description: Natural language description of the task
            session_id: Optional session identifier
        
        Returns:
            Dict containing task execution results
        """
        if session_id:
            self.session_manager.set_current_session(session_id)
        
        # Publish task start event
        self.event_bus.publish("TASK_STARTED", {
            "session_id": session_id,
            "task_description": task_description
        })
        
        try:
            # Decompose task into steps
            steps = await self.decomposer.decompose_task(task_description)
            
            # Execute steps through controller
            result = await self.controller.execute_steps(steps)
            
            # Publish task completion event
            self.event_bus.publish("TASK_COMPLETED", {
                "task_id": result.get("task_id"),
                "success": True,
                "result": result
            })
            
            return result
            
        except Exception as e:
            # Publish error event
            self.event_bus.publish("ERROR_OCCURRED", {
                "message": str(e),
                "source": "agent_hub",
                "task_description": task_description
            })
            raise
