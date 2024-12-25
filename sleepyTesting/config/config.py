"""Configuration module for sleepyTesting framework.

This module provides configuration options for:
1. Platform selection (android/ios/web)
2. Framework selection (uiautomator2/appium/selenium)
3. Device management and validation
4. LLM integration settings
   - OpenAI API key management
   - Model selection and parameters
   - Rate limiting and throttling
   - Concurrent request handling

Environment Variables:
    Platform & Framework:
        SLEEPYTESTING_PLATFORM: Platform to use (android/ios/web)
        SLEEPYTESTING_FRAMEWORK: Framework to use (uiautomator2/appium/selenium)
        
    Device Configuration:
        SLEEPYTESTING_ANDROID_DEVICE: Android device ID
        SLEEPYTESTING_IOS_DEVICE: iOS device ID
        SLEEPYTESTING_ALLOWED_ANDROID_DEVICES: Comma-separated list of allowed Android devices
        SLEEPYTESTING_ALLOWED_IOS_DEVICES: Comma-separated list of allowed iOS devices
        
    LLM Configuration:
        OPENAI_API_KEY: OpenAI API key (required)
        SLEEPYTESTING_LLM_MODEL: Model to use (default: gpt-4)
        SLEEPYTESTING_LLM_TEMPERATURE: Sampling temperature (default: 0.7)
        SLEEPYTESTING_LLM_MAX_TOKENS: Maximum tokens per request (default: 2000)
        
    Rate Limiting:
        SLEEPYTESTING_LLM_MAX_RETRIES: Maximum retry attempts (default: 3)
        SLEEPYTESTING_LLM_MIN_RETRY_WAIT: Minimum retry wait time in seconds (default: 1.0)
        SLEEPYTESTING_LLM_MAX_RETRY_WAIT: Maximum retry wait time in seconds (default: 60.0)
        SLEEPYTESTING_LLM_MAX_CONCURRENT: Maximum concurrent requests (default: 5)
        SLEEPYTESTING_LLM_RATE_LIMIT: Maximum requests per period (default: 50)
        SLEEPYTESTING_LLM_RATE_PERIOD: Rate limit period in seconds (default: 60)
        
    Other:
        SLEEPYTESTING_TIMEOUT: Default timeout for UI operations in seconds (default: 30)
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
    """Validate and return platform type.

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
    for d in os.getenv(
        "SLEEPYTESTING_ALLOWED_ANDROID_DEVICES", ""
    ).split(",")
    if d.strip()
]
ALLOWED_IOS_DEVICES: List[str] = [
    d.strip()
    for d in os.getenv(
        "SLEEPYTESTING_ALLOWED_IOS_DEVICES", ""
    ).split(",")
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

# LLM Configuration
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable must be set. "
        "Get your API key from https://platform.openai.com/account/api-keys"
    )

# Model configuration
LLM_MODEL: str = os.getenv("SLEEPYTESTING_LLM_MODEL", "gpt-4")
LLM_TEMPERATURE: float = float(os.getenv("SLEEPYTESTING_LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS: int = int(os.getenv("SLEEPYTESTING_LLM_MAX_TOKENS", "2000"))

# Rate limiting configuration
LLM_MAX_RETRIES: int = int(os.getenv("SLEEPYTESTING_LLM_MAX_RETRIES", "3"))
LLM_MIN_RETRY_WAIT: float = float(
    os.getenv("SLEEPYTESTING_LLM_MIN_RETRY_WAIT", "1.0")
)
LLM_MAX_RETRY_WAIT: float = float(
    os.getenv("SLEEPYTESTING_LLM_MAX_RETRY_WAIT", "60.0")
)
LLM_MAX_CONCURRENT_REQUESTS: int = int(
    os.getenv("SLEEPYTESTING_LLM_MAX_CONCURRENT", "5")
)

# Request throttling (in seconds)
LLM_REQUEST_TIMEOUT: float = float(
    os.getenv("SLEEPYTESTING_LLM_TIMEOUT", "30.0")
)
LLM_RATE_LIMIT_REQUESTS: int = int(
    os.getenv("SLEEPYTESTING_LLM_RATE_LIMIT", "50")
)
LLM_RATE_LIMIT_PERIOD: int = int(
    os.getenv("SLEEPYTESTING_LLM_RATE_PERIOD", "60")
)

# Other configuration
# Default 30 seconds timeout for UI operations
TIMEOUT: int = int(os.getenv("SLEEPYTESTING_TIMEOUT", "30"))
