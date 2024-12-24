"""Task Decomposition Agent - Breaks down high-level UI tasks into atomic
operations"""
import os
import re
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
    device_id: Optional[str] = None  # Device ID for multi-device scenarios


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
            "在Android设备A123上发送短信，在iOS设备B456上查收短信" ->
            [UIStep(action="send_sms", platform="android", device_id="A123", ...),
             UIStep(action="check_sms", platform="ios", device_id="B456", ...)]
        """
        # TODO: Implement full LLM-based task decomposition
        steps = []
        
        # Split task into subtasks for multi-device operations
        subtasks = [s.strip() for s in task_description.split('，')]
        
        for subtask in subtasks:
            # Platform and device detection
            platform = None
            device_id = None
            
            # Check for Android platform and device
            if "Android" in subtask or "安卓" in subtask:
                platform = "android"
                # Look for device ID patterns
                if "设备" in subtask:
                    # Extract ID after "设备"
                    parts = subtask.split("设备")
                    if len(parts) > 1:
                        # Extract alphanumeric ID
                        import re
                        matches = re.findall(r'([A-Za-z0-9]+)', parts[1])
                        if matches:
                            device_id = matches[0]
                elif "device" in subtask.lower():
                    # Extract ID after "device"
                    parts = subtask.lower().split("device")
                    if len(parts) > 1:
                        # Extract alphanumeric ID
                        import re
                        matches = re.findall(r'([A-Za-z0-9]+)', parts[1])
                        if matches:
                            device_id = matches[0]
                
                # Default device ID if none specified
                device_id = device_id or os.getenv("SLEEPYTESTING_ANDROID_DEVICE", "default-android")
                
                # Create Android step
                steps.append(UIStep(
                    action="send_sms" if "发送" in subtask else "check_sms",
                    platform=platform,
                    device_id=device_id,
                    description=f"Perform action on Android device {device_id}"
                ))
            
            # Check for iOS platform and device
            elif "iOS" in subtask or "苹果" in subtask:
                platform = "ios"
                # Look for device ID patterns
                if "设备" in subtask:
                    parts = subtask.split("设备")
                    if len(parts) > 1:
                        # Extract alphanumeric ID
                        import re
                        matches = re.findall(r'([A-Za-z0-9]+)', parts[1])
                        if matches:
                            device_id = matches[0]
                elif "device" in subtask.lower():
                    parts = subtask.lower().split("device")
                    if len(parts) > 1:
                        # Extract alphanumeric ID
                        import re
                        matches = re.findall(r'([A-Za-z0-9]+)', parts[1])
                        if matches:
                            device_id = matches[0]
                
                # Default device ID if none specified
                device_id = device_id or os.getenv("SLEEPYTESTING_IOS_DEVICE", "default-ios")
                
                
                # Create iOS step
                steps.append(UIStep(
                    action="check_sms" if "查收" in subtask else "send_sms",
                    platform=platform,
                    device_id=device_id,
                    description=f"Perform action on iOS device {device_id}"
                ))

        return steps

    def validate_steps(
        self,
        steps: List[UIStep]
    ) -> bool:
        """Validate that the decomposed steps are valid and complete

        Args:
            steps: List of UIStep objects to validate

        Returns:
            bool indicating if steps are valid
        """
        if not steps:
            return False
        return all(isinstance(step, UIStep) for step in steps)
