"""
Configuration module for sleepyTesting framework
"""
import os
from typing import Literal, Optional

# Platform types
PlatformType = Literal["android", "ios", "web"]
VALID_PLATFORMS = ["android", "ios", "web"]

# Framework types
FrameworkType = Literal["uiautomator2", "appium", "selenium"]
VALID_FRAMEWORKS = ["uiautomator2", "appium", "selenium"]

def validate_platform(platform: str) -> PlatformType:
    """
    Validate and return platform type
    
    Args:
        platform: Platform string to validate
        
    Returns:
        Validated platform type
        
    Raises:
        ValueError: If platform is not valid
    """
    if platform not in VALID_PLATFORMS:
        raise ValueError(f"Invalid platform: {platform}. Must be one of {VALID_PLATFORMS}")
    return platform  # type: ignore

def validate_framework(framework: str) -> FrameworkType:
    """
    Validate and return framework type
    
    Args:
        framework: Framework string to validate
        
    Returns:
        Validated framework type
        
    Raises:
        ValueError: If framework is not valid
    """
    if framework not in VALID_FRAMEWORKS:
        raise ValueError(f"Invalid framework: {framework}. Must be one of {VALID_FRAMEWORKS}")
    return framework  # type: ignore

# Default configuration
PLATFORM: PlatformType = validate_platform(os.getenv("SLEEPYTESTING_PLATFORM", "android"))
FRAMEWORK: FrameworkType = validate_framework(os.getenv("SLEEPYTESTING_FRAMEWORK", "uiautomator2"))

# Additional configuration options can be added here
DEVICE_IDENTIFIER: Optional[str] = os.getenv("SLEEPYTESTING_DEVICE_ID")
TIMEOUT: int = int(os.getenv("SLEEPYTESTING_TIMEOUT", "30"))  # Default 30 seconds timeout
