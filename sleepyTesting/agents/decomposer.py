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

    def parse_device_id(self, text: str, platform: str) -> Optional[str]:
        """Parse device ID from text for a specific platform.

        Args:
            text: Text to parse device ID from
            platform: Platform type ('android' or 'ios')

        Returns:
            Device ID if found, otherwise None

        Example:
            parse_device_id("在Android设备A123上发送短信", "android") -> "A123"
            parse_device_id("Send SMS on iOS device B456", "ios") -> "B456"
        """
        # Check for Chinese device identifier
        if "设备" in text:
            parts = text.split("设备")
            if len(parts) > 1:
                matches = re.findall(r'([A-Za-z0-9]+)', parts[1])
                if matches:
                    return matches[0]

        # Check for English device identifier
        if "device" in text.lower():
            parts = text.lower().split("device")
            if len(parts) > 1:
                matches = re.findall(r'([A-Za-z0-9]+)', parts[1])
                if matches:
                    return matches[0]

        # Get default from environment
        env_var = f"SLEEPYTESTING_{platform.upper()}_DEVICE"
        return os.getenv(env_var, f"default-{platform}")

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
            # Platform detection
            platform = None
            
            # Check for Android platform
            if "Android" in subtask or "安卓" in subtask:
                platform = "android"
                device_id = self.parse_device_id(subtask, platform)
                
                # Create Android step
                steps.append(UIStep(
                    action="send_sms" if "发送" in subtask else "check_sms",
                    platform=platform,
                    device_id=device_id,
                    description=f"Perform action on Android device {device_id}"
                ))
            
            # Check for iOS platform
            elif "iOS" in subtask or "苹果" in subtask:
                platform = "ios"
                device_id = self.parse_device_id(subtask, platform)
                
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
