"""
UI Automator2 driver implementation
"""
import uiautomator2 as u2
from typing import Optional, Tuple, Any
from .driver_interface import BaseDriver


class UIAutomatorDriver(BaseDriver):
    """Android UI Automator2 driver implementation"""

    def connect(self, device_identifier: Optional[str] = None) -> None:
        """
        Connect to an Android device

        Args:
            device_identifier: Optional device serial number
        """
        self.device = (
            u2.connect(device_identifier)
            if device_identifier
            else u2.connect()
        )

    def click(
        self,
        element_id: Optional[str] = None,
        coordinates: Optional[Tuple[int, int]] = None
    ) -> None:
        """
        Click on an element or coordinates

        Args:
            element_id: Optional element identifier (resource ID)
            coordinates: Optional (x, y) coordinates
        """
        if element_id:
            self.device(resourceId=element_id).click()
        elif coordinates:
            x, y = coordinates
            self.device.click(x, y)

    def get_element(self, element_id: str) -> Any:
        """
        Get UI element by resource ID

        Args:
            element_id: Element resource ID

        Returns:
            UI element object
        """
        return self.device(resourceId=element_id)

    def type_text(self, text: str, element_id: Optional[str] = None) -> None:
        """
        Type text into an element or at current focus

        Args:
            text: Text to type
            element_id: Optional element resource ID to type into
        """
        if element_id:
            self.device(resourceId=element_id).set_text(text)
        else:
            self.device.set_text(text)

    def is_element_present(self, element_id: str) -> bool:
        """
        Check if an element is present on the screen

        Args:
            element_id: Element resource ID to check

        Returns:
            True if element is present, False otherwise
        """
        return self.device(resourceId=element_id).exists
