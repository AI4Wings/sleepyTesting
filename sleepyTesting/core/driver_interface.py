"""
Driver interface for UI automation frameworks
"""
from typing import Optional, Tuple, Any
from abc import ABC, abstractmethod


class BaseDriver(ABC):
    """
    Abstract base class for UI automation drivers.
    All platform-specific drivers (Android, iOS, Web) must implement this
    interface.
    """

    @abstractmethod
    def connect(self, device_identifier: Optional[str] = None) -> None:
        """
        Connect to a device or browser instance

        Args:
            device_identifier: Optional identifier for the target
                device/browser
        """
        pass

    @abstractmethod
    def click(
        self,
        element_id: Optional[str] = None,
        coordinates: Optional[Tuple[int, int]] = None
    ) -> None:
        """
        Click on an element or coordinates

        Args:
            element_id: Optional element identifier (varies by platform)
            coordinates: Optional (x, y) coordinates for direct click
        """
        pass

    @abstractmethod
    def get_element(self, element_id: str) -> Any:
        """
        Get a UI element by its identifier

        Args:
            element_id: Element identifier (varies by platform)

        Returns:
            Platform-specific element object
        """
        pass

    @abstractmethod
    def type_text(
        self,
        text: str,
        element_id: Optional[str] = None
    ) -> None:
        """
        Type text into an element or at current focus

        Args:
            text: Text to type
            element_id: Optional element identifier to type into
        """
        pass

    @abstractmethod
    def is_element_present(self, element_id: str) -> bool:
        """
        Check if an element is present on the screen

        Args:
            element_id: Element identifier to check

        Returns:
            True if element is present, False otherwise
        """
        pass
