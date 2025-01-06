"""
Core data models used across the sleepyTesting framework.
"""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class UIStep(BaseModel):
    """
    Model for a single UI automation step.
    
    This model represents either a UI action or an external tool call.
    For UI actions, the action and target fields are required.
    For tool calls, the tool_name field indicates which tool to use.
    """

    action: str = Field(
        ...,
        description="The action to perform (click, type, swipe, etc)"
    )
    target: str = Field(
        ...,
        description="The target element or coordinates"
    )
    platform: str = Field(
        ...,
        description="Target platform (android/ios/web)"
    )
    device_id: Optional[str] = Field(
        None,
        description="Specific device ID if needed"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters"
    )
    description: str = Field(
        ...,
        description="Human readable description of the step"
    )
    # External tool integration fields
    tool_name: Optional[str] = Field(
        None,
        description="Name of the external tool to call"
    )
    tool_params: Optional[Dict[str, Any]] = Field(
        None,
        description="Parameters to pass to the external tool"
    )
