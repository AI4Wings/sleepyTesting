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
            
        step_key = f"{step.action}:{step.element_id or step.coordinates}"
        self.history[step_key] = {
            "description": step.description,
            "success_count": self.history.get(step_key, {}).get("success_count", 0) + 1
        }
        
        self._save_history()
        
    def optimize_steps(self, steps: List[UIStep]) -> Optional[List[UIStep]]:
        """
        Optimize steps based on historical patterns
        
        Args:
            steps: List of planned UI steps
            
        Returns:
            Optimized list of steps if available
        """
        # TODO: Implement step optimization logic
        # This could include:
        # 1. Removing redundant steps
        # 2. Replacing with known successful patterns
        # 3. Adjusting timing based on history
        return steps
        
    def _save_history(self):
        """Save task history to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.history, f)