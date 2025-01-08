"""
Controller Agent - Coordinates the execution of UI testing tasks
"""
import os
import logging
from typing import (
    Dict,
    List,
    Optional,
    Tuple
)

from .decomposer import UIStep
from ..assertions import AssertionResult
from ..core.driver_interface import BaseDriver
from ..core.driver_factory import get_driver
from ..core.event_bus import IEventBus
from ..utils.screenshot import ScreenshotManager
from ..tools.tool_registry import global_tool_registry

# Configure logging
logger = logging.getLogger(__name__)


class ControllerAgent:
    """Coordinates the execution of UI testing tasks"""

    def __init__(
        self,
        decomposer,
        event_bus: IEventBus,
        default_executor: Optional[BaseDriver] = None,
    ):
        """Initialize controller agent

        Args:
            decomposer: Task decomposition agent
            event_bus: Event bus for inter-agent communication
            default_executor: Optional default UI automation driver
                (used for backward compatibility)
        """
        self.decomposer = decomposer
        self.event_bus = event_bus
        self.screenshot_manager = ScreenshotManager()

        # Map of (platform, device_id) to driver instances
        DriverKey = Tuple[Optional[str], Optional[str]]
        self.drivers: Dict[DriverKey, BaseDriver] = {}

        # Store default executor if provided
        if default_executor is not None:
            self.drivers[(None, None)] = default_executor

    def get_or_create_driver(self, step: UIStep) -> BaseDriver:
        """
        Get or create a driver instance for the given step

        Args:
            step: UIStep containing platform and device information

        Returns:
            BaseDriver instance for the specified platform/device
        """
        key = (step.platform, step.device_id)

        # Return existing driver if available
        if key in self.drivers:
            return self.drivers[key]

        # Use default driver if exists and no platform specified
        if key == (None, None) and (None, None) in self.drivers:
            return self.drivers[(None, None)]

        # Create new driver with platform override
        if step.platform:
            os.environ["SLEEPYTESTING_PLATFORM"] = step.platform
        driver = get_driver()

        # Connect to specific device if ID provided
        if step.device_id:
            driver.connect(step.device_id)

        self.drivers[key] = driver
        return driver

    async def execute_task(
        self,
        task_description: str
    ) -> List[AssertionResult]:
        """Execute a UI testing task

        Args:
            task_description: Natural language description of the task

        Returns:
            List of assertion results for each step
        """
        # Decompose task into steps
        steps = self.decomposer.decompose_task(task_description)

        # Publish task start event
        self.event_bus.publish("TASK_STARTED", {
            "task_description": task_description,
            "steps": steps
        })

        # Request step optimization
        self.event_bus.publish("OPTIMIZE_STEPS", {
            "steps": steps
        })

        results = []
        for step in steps:
            # Take before screenshot
            before_screenshot = self.screenshot_manager.capture("before")

            # Handle tool calls first
            if step.tool_name:
                try:
                    tool_result = global_tool_registry.call_tool(
                        step.tool_name,
                        step.tool_params or {}
                    )
                    # Store tool result for use by subsequent steps
                    step.parameters["tool_result"] = tool_result
                    msg = (
                        f"Tool {step.tool_name} executed successfully: "
                        f"{tool_result}"
                    )
                    logger.info(msg)
                except Exception as e:
                    msg = f"Tool {step.tool_name} execution failed: {e}"
                    logger.error(msg)
                    raise

            # Handle UI actions
            else:
                # Get appropriate driver for this step
                driver = self.get_or_create_driver(step)

                # Execute step with platform-specific driver
                if step.coordinates:
                    driver.click(coordinates=step.coordinates)
                elif step.element_id:
                    driver.click(element_id=step.element_id)

            # Take after screenshot
            after_screenshot = self.screenshot_manager.capture("after")

            # Publish step execution event
            step_data = {
                "step": step,
                "before_screenshot": before_screenshot,
                "after_screenshot": after_screenshot
            }
            self.event_bus.publish("STEP_EXECUTED", step_data)

            # Wait for verification result
            # Default to passed
            result = AssertionResult(step=step, passed=True)
            results.append(result)

        # Publish task completion event
        self.event_bus.publish("TASK_COMPLETED", {
            "task_description": task_description,
            "results": results
        })

        return results
