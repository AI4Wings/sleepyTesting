"""
Controller Agent - Coordinates the execution of UI testing tasks
"""
import os
from typing import List, Optional, Dict, Tuple
from .decomposer import UIStep
from ..assertions import AssertionResult
from ..core.driver_interface import BaseDriver
from ..core.driver_factory import get_driver
from ..utils.screenshot import ScreenshotManager

class ControllerAgent:
    """Coordinates the execution of UI testing tasks"""
    
    def __init__(self, decomposer, default_executor: Optional[BaseDriver] = None, supervisor=None, memory=None):
        """
        Initialize controller agent
        
        Args:
            decomposer: Task decomposition agent
            default_executor: Optional default UI automation driver (used for backward compatibility)
            supervisor: Optional supervision agent
            memory: Optional memory agent
        """
        self.decomposer = decomposer
        self.supervisor = supervisor
        self.memory = memory
        self.screenshot_manager = ScreenshotManager()
        self.drivers: Dict[Tuple[Optional[str], Optional[str]], BaseDriver] = {}
        
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
        
    async def execute_task(self, task_description: str) -> List[AssertionResult]:
        """
        Execute a UI testing task
        
        Args:
            task_description: Natural language description of the task
            
        Returns:
            List of assertion results for each step
        """
        # Decompose task into steps
        steps = self.decomposer.decompose_task(task_description)
        
        # Check memory for similar tasks
        if self.memory:
            optimized_steps = self.memory.optimize_steps(steps)
            if optimized_steps:
                steps = optimized_steps
        
        results = []
        for step in steps:
            # Take before screenshot
            before_screenshot = self.screenshot_manager.capture("before")
            
            # Get appropriate driver for this step
            driver = self.get_or_create_driver(step)
            
            # Execute step with platform-specific driver
            if step.coordinates:
                driver.click(coordinates=step.coordinates)
            elif step.element_id:
                driver.click(element_id=step.element_id)
            
            # Take after screenshot
            after_screenshot = self.screenshot_manager.capture("after")
            
            # Verify step execution
            if self.supervisor:
                result = self.supervisor.verify_step(
                    step, before_screenshot, after_screenshot
                )
                results.append(result)
                
                # Store successful steps in memory
                if result.passed and self.memory:
                    self.memory.store_step(step, result)
        
        return results
