"""
Driver factory module for sleepyTesting framework
"""
from typing import Dict, Type

from .driver_interface import BaseDriver
from .uiautomator import UIAutomatorDriver
from .ios_driver import iOSDriver
from .web_driver import WebDriver
from ..config.config import PLATFORM, FRAMEWORK, PlatformType, FrameworkType

# Platform to driver mapping
PLATFORM_DRIVERS: Dict[PlatformType, Dict[FrameworkType, Type[BaseDriver]]] = {
    "android": {
        "uiautomator2": UIAutomatorDriver,
        # "appium": AppiumAndroidDriver,  # Future implementation
    },
    "ios": {
        "appium": iOSDriver,  # Currently placeholder
    },
    "web": {
        "selenium": WebDriver,  # Currently placeholder
    }
}

def get_driver() -> BaseDriver:
    """
    Get appropriate driver instance based on configured platform and framework
    
    Returns:
        BaseDriver: Instance of appropriate driver for configured platform/framework
        
    Raises:
        ValueError: If platform/framework combination is not supported
    """
    try:
        framework_drivers = PLATFORM_DRIVERS[PLATFORM]
    except KeyError:
        raise ValueError(f"Unsupported platform: {PLATFORM}")


    try:
        driver_class = framework_drivers[FRAMEWORK]
    except KeyError:
        raise ValueError(
            f"Unsupported framework '{FRAMEWORK}' for platform '{PLATFORM}'. "
            f"Supported frameworks: {list(framework_drivers.keys())}"
        )
        
    return driver_class()
