"""
Controller Agent - Coordinates the execution of UI testing tasks
"""
from typing import List, Optional
from .decomposer import UIStep
from ..assertions import AssertionResult
from ..core.driver_interface import BaseDriver
from ..core.driver_factory import get_driver
from ..utils.screenshot import ScreenshotManager

class ControllerAgent:
    """Coordinates the execution of UI testing tasks"""
    
    def __init__(self, decomposer, executor: Optional[BaseDriver] = None, supervisor=None, memory=None):
        """
        Initialize controller agent
        
        Args:
            decomposer: Task decomposition agent
            executor: Optional UI automation driver (uses configured driver if None)
            supervisor: Optional supervision agent
            memory: Optional memory agent
        """
        self.decomposer = decomposer
        self.executor = executor if executor is not None else get_driver()
        self.supervisor = supervisor
        self.memory = memory
        self.screenshot_manager = ScreenshotManager()
        
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
            
            # Execute step
            if step.coordinates:
                self.executor.click(coordinates=step.coordinates)
            elif step.element_id:
                self.executor.click(element_id=step.element_id)
            
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
