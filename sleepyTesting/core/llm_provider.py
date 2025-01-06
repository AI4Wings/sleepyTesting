"""
LLM provider interface and implementations for the sleepyTesting framework.

This module defines the interface for LLM providers and includes the OpenAI
implementation. The interface allows for easy swapping of LLM backends while
maintaining consistent behavior.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from .models import UIStep


class ILLMProvider(ABC):
    """Interface defining the contract for LLM providers."""
    
    @abstractmethod
    async def generate_steps(self, task_description: str) -> Dict[str, Any]:
        """
        Generate UI automation steps from a task description.
        
        Args:
            task_description: Natural language description of the task
            
        Returns:
            Dictionary containing:
                - steps: List[UIStep] - The generated automation steps
                - devices: List[Tuple[str, str]] - Required devices (platform, id)
                - original_task: str - The input task description
                
        Raises:
            ValueError: If response validation fails
            Exception: If LLM API call fails
        """
        pass
    
    @abstractmethod
    def extract_device_info(self, task: str) -> List[Tuple[str, str]]:
        """
        Extract device IDs and platforms from task description.
        
        Args:
            task: Natural language task description
            
        Returns:
            List of (platform, device_id) tuples
        """
        pass


class OpenAIProvider(ILLMProvider):
    """OpenAI-based implementation of the LLM provider interface."""
    
    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 5,
        max_concurrent_requests: int = 5
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            model: Name of the model to use (default: gpt-4)
            api_key: Optional API key (defaults to env var)
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Maximum tokens in response (default: 2000)
            max_retries: Maximum number of retries
            max_concurrent_requests: Maximum concurrent API requests
        """
        from .llm import LLMClient
        self._client = LLMClient(
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            max_concurrent_requests=max_concurrent_requests
        )
    
    async def generate_steps(self, task_description: str) -> Dict[str, Any]:
        """Generate UI steps. See ILLMProvider.generate_steps."""
        return await self._client.generate_steps(task_description)
    
    def extract_device_info(self, task: str) -> List[Tuple[str, str]]:
        """Extract device info. See ILLMProvider.extract_device_info."""
        return self._client._extract_device_info(task)
