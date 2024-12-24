"""
UI Automator2 integration module
"""
import uiautomator2 as u2
from typing import Optional, Tuple

class UIAutomator:
    """Wrapper for UI Automator2"""
    
    def __init__(self, device_serial: Optional[str] = None):
        """
        Initialize UI Automator
        
        Args:
            device_serial: Optional device serial number
        """
        self.device = u2.connect(device_serial) if device_serial else u2.connect()
        
    def click(self, element_id: Optional[str] = None, coordinates: Optional[Tuple[int, int]] = None):
        """
        Click on an element or coordinates
        
        Args:
            element_id: Optional element identifier
            coordinates: Optional (x, y) coordinates
        """
        if element_id:
            self.device(resourceId=element_id).click()
        elif coordinates:
            x, y = coordinates
            self.device.click(x, y)
            
    def get_element(self, element_id: str):
        """
        Get UI element by ID
        
        Args:
            element_id: Element identifier
            
        Returns:
            UI element object
        """
        return self.device(resourceId=element_id)
