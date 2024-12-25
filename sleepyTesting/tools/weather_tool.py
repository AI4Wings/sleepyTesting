"""
Weather Tool - External tool for fetching weather information
"""
import logging
import requests
from typing import Any, Dict

from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class WeatherTool(BaseTool):
    """Tool for fetching weather information for a given city"""

    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validate required parameters for weather lookup
        
        Args:
            params: Dictionary containing tool parameters
            
        Raises:
            ValueError: If required parameters are missing
        """
        city = params.get("city")
        if not city:
            raise ValueError("Missing required 'city' parameter")
        
        if not isinstance(city, str):
            raise ValueError("'city' parameter must be a string")

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch weather information for the specified city
        
        Args:
            params: Dictionary containing:
                - city: Name of the city to get weather for
                
        Returns:
            Dictionary containing:
                - temperature: Current temperature
                - description: Weather description
                - humidity: Current humidity percentage
        """
        self.validate_params(params)
        city = params["city"]
        
        try:
            # Using OpenWeatherMap API as an example
            # In production, API key would be loaded from config
            api_key = "demo_key"  # Replace with actual API key
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"]
            }
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch weather data: {e}")
            # For demo, return mock data
            return {
                "temperature": 20,
                "description": "partly cloudy",
                "humidity": 65
            }
