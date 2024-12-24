"""
Memory Agent - Stores and retrieves historical task execution patterns
"""
from typing import List, Optional, Dict
from .decomposer import UIStep
from ..assertions import AssertionResult
import json
import os

class MemoryAgent:
    """Stores and retrieves historical task execution patterns"""
    
    def __init__(self, storage_path: str = "task_history.json"):
        """
        Initialize memory agent
        
        Args:
            storage_path: Path to store task history
        """
        self.storage_path = storage_path
        self.history: Dict = self._load_history()
        
    def _load_history(self) -> Dict:
        """Load task history from storage"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}
        
    def store_step(self, step: UIStep, result: AssertionResult):
        """
        Store successful step execution
        
        Args:
            step: Executed UI step
            result: Assertion result of the step
        """
        if not result.passed:
            return
            
        # Generate device-aware step key
        step_key = (
            f"{step.platform or 'default'}:"
            f"{step.device_id or 'default'}:"
            f"{step.action}:{step.element_id or step.coordinates}"
        )
        
        # Store step with device-specific metadata
        self.history[step_key] = {
            "description": step.description,
            "platform": step.platform,
            "device_id": step.device_id,
            "success_count": self.history.get(step_key, {}).get("success_count", 0) + 1,
            "last_success": True  # Flag for pattern learning
        }
        
        self._save_history()
        
    def optimize_steps(self, steps: List[UIStep]) -> Optional[List[UIStep]]:
        """
        Optimize steps based on historical patterns, considering device-specific patterns
        
        Args:
            steps: List of planned UI steps
            
        Returns:
            Optimized list of steps if available
        """
        optimized_steps = []
        
        for step in steps:
            # Generate device-specific key
            step_key = (
                f"{step.platform or 'default'}:"
                f"{step.device_id or 'default'}:"
                f"{step.action}:{step.element_id or step.coordinates}"
            )
            
            # Check for device-specific patterns
            if step_key in self.history:
                pattern = self.history[step_key]
                if pattern["success_count"] > 0 and pattern["last_success"]:
                    # Use the successful pattern
                    optimized_step = UIStep(
                        action=step.action,
                        element_id=step.element_id,
                        coordinates=step.coordinates,
                        description=pattern["description"],
                        platform=pattern["platform"],
                        device_id=pattern["device_id"]
                    )
                    optimized_steps.append(optimized_step)
                    continue
                    
            # If no pattern found or pattern not successful, keep original step
            optimized_steps.append(step)
            
        return optimized_steps
        
    def _save_history(self):
        """Save task history to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.history, f)
