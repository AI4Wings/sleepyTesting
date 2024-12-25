"""
Configuration module for sleepyTesting framework
"""
import os
from typing import List, Literal, Optional

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
        raise ValueError(
            f"Invalid platform: {platform}. Must be one of {VALID_PLATFORMS}"
        )
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
        raise ValueError(
            f"Invalid framework: {framework}. Must be one of {VALID_FRAMEWORKS}"
        )
    return framework  # type: ignore

# Default configuration
PLATFORM: PlatformType = validate_platform(
    os.getenv("SLEEPYTESTING_PLATFORM", "android")
)
FRAMEWORK: FrameworkType = validate_framework(
    os.getenv("SLEEPYTESTING_FRAMEWORK", "uiautomator2")
)

# Device configuration
ANDROID_DEVICE_ID: Optional[str] = os.getenv("SLEEPYTESTING_ANDROID_DEVICE")
IOS_DEVICE_ID: Optional[str] = os.getenv("SLEEPYTESTING_IOS_DEVICE")
DEVICE_IDENTIFIER: Optional[str] = os.getenv(
    "SLEEPYTESTING_DEVICE_ID"
)  # Legacy support

# Whitelisted device IDs (optional)
ALLOWED_ANDROID_DEVICES: List[str] = [
    d.strip()
    for d in os.getenv("SLEEPYTESTING_ALLOWED_ANDROID_DEVICES", "").split(",")
    if d.strip()
]
ALLOWED_IOS_DEVICES: List[str] = [
    d.strip()
    for d in os.getenv("SLEEPYTESTING_ALLOWED_IOS_DEVICES", "").split(",")
    if d.strip()
]


def validate_device_id(device_id: Optional[str], platform: str) -> Optional[str]:
    """Validate device ID for a specific platform.

    Args:
        device_id: Device ID to validate
        platform: Platform type ('android' or 'ios')

    Returns:
        Validated device ID or None if no ID provided

    Raises:
        ValueError: If device ID is not in allowed list when whitelist is configured
    """
    if not device_id:
        return None

    # Check platform-specific whitelist
    allowed_devices = {
        "android": ALLOWED_ANDROID_DEVICES,
        "ios": ALLOWED_IOS_DEVICES
    }.get(platform, [])

    if allowed_devices and device_id not in allowed_devices:
        raise ValueError(
            f"Device ID '{device_id}' not in allowed list for {platform}: "
            f"{allowed_devices}"
        )

    return device_id

# Other configuration
# Default 30 seconds timeout
TIMEOUT: int = int(os.getenv("SLEEPYTESTING_TIMEOUT", "30"))
