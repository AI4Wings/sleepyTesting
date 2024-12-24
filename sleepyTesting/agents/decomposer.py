"""
Task Decomposition Agent - Breaks down high-level UI tasks into atomic operations
"""
from typing import List, Optional
from pydantic import BaseModel

class UIStep(BaseModel):
    """Represents a single UI operation step"""
    action: str
    element_id: Optional[str] = None
    text: Optional[str] = None
    coordinates: Optional[tuple[int, int]] = None
    description: str
    
    # Device/platform specific fields
    platform: Optional[str] = None  # e.g., 'android', 'ios', 'web'
    device_id: Optional[str] = None  # Device identifier for multi-device scenarios

class TaskDecomposer:
    """Decomposes high-level tasks into specific UI steps using LLM"""
    
    def __init__(self, llm_client=None):
        """Initialize with optional LLM client"""
        self.llm_client = llm_client
    
    def decompose_task(self, task_description: str) -> List[UIStep]:
        """
        Decompose a high-level task description into specific UI steps
        
        Args:
            task_description: Natural language description of the UI task
            
        Returns:
            List of UIStep objects representing atomic operations
            
        Example:
            "在Android手机上发送短信，在iOS手机上查收短信" ->
            [UIStep(action="send_sms", platform="android", ...),
             UIStep(action="check_sms", platform="ios", ...)]
        """
        # TODO: Implement full LLM-based task decomposition
        # For now, implement basic platform/device detection
        steps = []
        
        # Simple keyword-based platform detection
        if "Android" in task_description or "安卓" in task_description:
            # Example: Send SMS step for Android
            steps.append(UIStep(
                action="send_sms",
                platform="android",
                device_id="default-android",  # Could be configured or discovered
                description="Send SMS on Android device"
            ))
            
        if "iOS" in task_description or "苹果" in task_description:
            # Example: Check SMS step for iOS
            steps.append(UIStep(
                action="check_sms",
                platform="ios",
                device_id="default-ios",  # Could be configured or discovered
                description="Check SMS on iOS device"
            ))
            
        return steps

    def validate_steps(self, steps: List[UIStep]) -> bool:
        """
        Validate that the decomposed steps are valid and complete
        
        Args:
            steps: List of UIStep objects to validate
            
        Returns:
            bool indicating if steps are valid
        """
        if not steps:
            return False
        return all(isinstance(step, UIStep) for step in steps)
