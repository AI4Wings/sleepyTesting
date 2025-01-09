"""
Agent Hub for coordinating multiple agents in the sleepyTesting framework.

This module provides centralized management of all agents, handling their
initialization, coordination, and event subscriptions. It serves as the main
orchestrator for the multi-agent system.
"""
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from .controller import ControllerAgent
from .decomposer import TaskDecomposer
from .supervisor import SupervisorAgent
from .memory import MemoryAgent
from ..core.event_bus import IEventBus
from ..core.session_manager import ISessionManager
from ..core.llm_provider import ILLMProvider
from ..core.user_interface import IUserInterface


class AgentState(Enum):
    """States an agent can be in during its lifecycle."""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class AgentInfo:
    """Information about an agent instance."""
    id: str
    type: str
    state: AgentState
    last_heartbeat: datetime
    error_count: int = 0
    retry_count: int = 0


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

    def _initialize_agents(self) -> None:
        """Initialize all required agents with proper state tracking."""
        # Initialize with state tracking
        self.decomposer = self._register_agent(
            "decomposer",
            TaskDecomposer(self.llm_provider)
        )
        self.supervisor = self._register_agent(
            "supervisor",
            SupervisorAgent()
        )
        self.memory = self._register_agent(
            "memory",
            MemoryAgent()
        )
        self.controller = self._register_agent(
            "controller",
            ControllerAgent(
                decomposer=self.decomposer,
                supervisor=self.supervisor,
                memory=self.memory,
            )
        )

    def _register_agent(self, agent_id: str, agent: Any) -> Any:
        """
        Register an agent with the hub and initialize its state tracking.

        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance to register

        Returns:
            The registered agent instance
        """
        self.agents[agent_id] = agent
        self.agent_info[agent_id] = AgentInfo(
            id=agent_id,
            type=agent.__class__.__name__,
            state=AgentState.INITIALIZING,
            last_heartbeat=datetime.now()
        )
        
        # Transition to ready state
        self._update_agent_state(agent_id, AgentState.READY)
        return agent

    def _update_agent_state(
        self,
        agent_id: str,
        state: AgentState,
        error: Optional[Exception] = None
    ) -> None:
        """
        Update an agent's state and handle any state transition logic.

        Args:
            agent_id: ID of the agent to update
            state: New state to transition to
            error: Optional error that caused the state change
        """
        if agent_id not in self.agent_info:
            raise ValueError(f"Unknown agent: {agent_id}")

        info = self.agent_info[agent_id]
        old_state = info.state
        info.state = state
        info.last_heartbeat = datetime.now()

        if state == AgentState.ERROR:
            info.error_count += 1
            if error:
                self.user_interface.error(
                    f"Agent {agent_id} error: {str(error)}"
                )
            if info.error_count >= self.ERROR_THRESHOLD:
                self._handle_agent_failure(agent_id)

        # Log state transition
        self.user_interface.inform(
            f"Agent {agent_id} transitioned from {old_state} to {state}"
        )

    def _setup_event_subscriptions(self) -> None:
        """Set up event subscriptions for all managed agents."""
        # Core workflow events
        self.event_bus.subscribe("TASK_STARTED", self._on_task_started)
        self.event_bus.subscribe("TASK_COMPLETED", self._on_task_completed)
        self.event_bus.subscribe("STEP_EXECUTED", self._on_step_executed)
        self.event_bus.subscribe("ERROR_OCCURRED", self._on_error)

        # Memory-related events
        self.event_bus.subscribe("MEMORY_UPDATED", self._on_memory_updated)

        # Agent lifecycle events
        self.event_bus.subscribe("AGENT_ERROR", self._on_agent_error)
        self.event_bus.subscribe("AGENT_RECOVERED", self._on_agent_recovered)

    def _on_task_started(self, payload: Dict[str, Any]) -> None:
        """Handle task start event."""
        session_id = payload.get("session_id")
        task_id = payload.get("task_id")
        msg = f"Starting task {task_id} in session {session_id}"
        self.user_interface.inform(msg)

    def _on_task_completed(self, payload: Dict[str, Any]) -> None:
        """Handle task completion event."""
        task_id = payload.get("task_id")
        success = payload.get("success", False)
        if success:
            msg = f"Task {task_id} completed successfully"
            self.user_interface.inform(msg)
        else:
            msg = f"Task {task_id} completed with issues"
            self.user_interface.warn(msg)

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
        self.user_interface.error(
            f"Error in {source}: {error_msg}"
        )

    def _on_memory_updated(self, payload: Dict[str, Any]) -> None:
        """Handle memory update events."""
        memory_id = payload.get("memory_id")
        self.user_interface.inform(f"Memory updated: {memory_id}")

    def _handle_agent_failure(self, agent_id: str) -> None:
        """
        Handle an agent that has exceeded its error threshold.

        Args:
            agent_id: ID of the failed agent
        """
        info = self.agent_info[agent_id]
        if info.retry_count < self.MAX_RETRIES:
            info.retry_count += 1
            self.user_interface.warn(
                f"Attempting to restart agent {agent_id} "
                f"(attempt {info.retry_count}/{self.MAX_RETRIES})"
            )
            self._restart_agent(agent_id)
        else:
            self.user_interface.error(
                f"Agent {agent_id} has failed permanently after "
                f"{self.MAX_RETRIES} restart attempts"
            )
            self._update_agent_state(agent_id, AgentState.SHUTDOWN)

    def _restart_agent(self, agent_id: str) -> None:
        """
        Attempt to restart a failed agent.

        Args:
            agent_id: ID of the agent to restart
        """
        try:
            # Re-initialize the specific agent
            if agent_id == "decomposer":
                self.decomposer = self._register_agent(
                    agent_id,
                    TaskDecomposer(self.llm_provider)
                )
            elif agent_id == "supervisor":
                self.supervisor = self._register_agent(
                    agent_id,
                    SupervisorAgent()
                )
            elif agent_id == "memory":
                self.memory = self._register_agent(
                    agent_id,
                    MemoryAgent()
                )
            elif agent_id == "controller":
                self.controller = self._register_agent(
                    agent_id,
                    ControllerAgent(
                        decomposer=self.decomposer,
                        supervisor=self.supervisor,
                        memory=self.memory,
                    )
                )
            
            # Reset error count on successful restart
            self.agent_info[agent_id].error_count = 0
            self._update_agent_state(agent_id, AgentState.READY)
            
        except Exception as e:
            self.user_interface.error(
                f"Failed to restart agent {agent_id}: {str(e)}"
            )
            self._update_agent_state(agent_id, AgentState.ERROR, error=e)

    def _start_health_monitoring(self) -> None:
        """Start the health monitoring system for all agents."""
        # Subscribe to health check events
        self.event_bus.subscribe(
            "HEALTH_CHECK",
            self._handle_health_check
        )
        
        # Publish initial health check
        self._publish_health_check()


    def _handle_health_check(self, payload: Dict[str, Any]) -> None:
        """
        Handle health check events for all agents.

        Args:
            payload: Health check event data
        """
        for agent_id, info in self.agent_info.items():
            # Check if agent is responsive
            if (datetime.now() - info.last_heartbeat).seconds > self.HEALTH_CHECK_INTERVAL:
                self.user_interface.warn(
                    f"Agent {agent_id} has not responded to health check"
                )
                self._update_agent_state(agent_id, AgentState.ERROR)

    def _publish_health_check(self) -> None:
        """Publish a health check event."""
        self.event_bus.publish("HEALTH_CHECK", {
            "timestamp": datetime.now().isoformat(),
            "agents": {
                agent_id: {
                    "state": info.state.value,
                    "error_count": info.error_count,
                    "retry_count": info.retry_count
                }
                for agent_id, info in self.agent_info.items()
            }
        })

    def _on_agent_error(self, payload: Dict[str, Any]) -> None:
        """
        Handle agent error events.

        Args:
            payload: Agent error event data
        """
        agent_id = payload.get("agent_id")
        error_msg = payload.get("message", "Unknown error")
        
        if agent_id in self.agent_info:
            self._update_agent_state(
                agent_id,
                AgentState.ERROR,
                error=Exception(error_msg)
            )

    def _on_agent_recovered(self, payload: Dict[str, Any]) -> None:
        """
        Handle agent recovery events.

        Args:
            payload: Agent recovery event data
        """
        agent_id = payload.get("agent_id")
        if agent_id in self.agent_info:
            self._update_agent_state(agent_id, AgentState.READY)

    async def execute_task(
        self,
        task_description: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
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
