"""
Decoupled assertion system for UI testing
"""
from typing import Optional, Any
from pydantic import BaseModel
from enum import Enum

class AssertionType(Enum):
    """Types of assertions supported"""
    ELEMENT_EXISTS = "element_exists"
    ELEMENT_VISIBLE = "element_visible"
    ELEMENT_CLICKABLE = "element_clickable"
    PAGE_STATE = "page_state"
    CUSTOM = "custom"

class AssertionResult(BaseModel):
    """Result of an assertion check"""
    type: AssertionType
    passed: bool
    message: str
    screenshot_path: Optional[str] = None
    actual_value: Any = None
    expected_value: Any = None
    suggestion: Optional[str] = None
