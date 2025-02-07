"""
OpenAI-specific implementation of the LLM client for generating UI automation
steps.

This module provides the concrete implementation of the OpenAI API client with:
- Rate limiting and concurrent request management
- Exponential backoff retry logic
- Response validation and error handling
- Support for both Chinese and English input
"""
import os
import json
import logging
import asyncio
from typing import Any, Dict, List, Optional, Tuple
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from .models import UIStep

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with Language Models to generate UI automation
    steps"""

    # Rate limiting settings
    MAX_RETRIES = 5
    MIN_RETRY_WAIT = 1  # seconds
    MAX_RETRY_WAIT = 60  # seconds
    MAX_CONCURRENT_REQUESTS = 5

    # Semaphore for concurrent request limiting
    _request_semaphore: Optional[asyncio.Semaphore] = None

    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = MAX_RETRIES,
        max_concurrent_requests: int = MAX_CONCURRENT_REQUESTS
    ):
        """
        Initialize LLM client

        Args:
            model: Name of the model to use (default: gpt-4)
            api_key: Optional API key for OpenAI (defaults to env var)
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Maximum tokens in response (default: 2000)
            max_retries: Maximum number of retries for failed requests
            max_concurrent_requests: Maximum number of concurrent API requests
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries

        # Configure OpenAI
        if api_key:
            openai.api_key = api_key
        else:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            if not openai.api_key:
                msg = "OpenAI API key not found in environment variables"
                raise ValueError(msg)

        # Initialize rate limiting
        if not LLMClient._request_semaphore:
            LLMClient._request_semaphore = asyncio.Semaphore(
                max_concurrent_requests
            )

    def _extract_device_info(self, task: str) -> List[Tuple[str, str]]:
        """
        Extract device IDs and platforms from task description

        Args:
            task: Natural language task description

        Returns:
            List of (platform, device_id) tuples
        """
        # Basic pattern matching for common device identifiers
        devices = []

        # Look for Android device IDs
        if "android" in task.lower():
            # For now just assume Android if mentioned
            devices.append(("android", None))

        # Look for iOS device IDs
        if "ios" in task.lower() or "iphone" in task.lower():
            devices.append(("ios", None))

        # Look for web platform
        if "web" in task.lower() or "browser" in task.lower():
            devices.append(("web", None))

        # Default to Android if no platform detected
        return devices or [("android", None)]

    @retry(
        retry=retry_if_exception_type((
            openai.error.RateLimitError,
            openai.error.APIError,
            openai.error.ServiceUnavailableError,
            openai.error.Timeout
        )),
        wait=wait_exponential(
            multiplier=MIN_RETRY_WAIT,
            max=MAX_RETRY_WAIT
        ),
        stop=stop_after_attempt(MAX_RETRIES),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def _call_openai_with_retry(
        self,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Make an OpenAI API call with retry logic

        Args:
            messages: List of message dictionaries for the chat completion

        Returns:
            OpenAI API response

        Raises:
            openai.error.OpenAIError: If all retries fail
        """
        async with LLMClient._request_semaphore:
            return await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

    async def generate_steps(self, task_description: str) -> Dict[str, Any]:
        """
        Generate UI automation steps from task description

        Args:
            task_description: Natural language description of the task

        Returns:
            Dictionary containing:
                - steps: List[UIStep] - Generated steps
                - devices: List[Tuple[str, str]] - Required (platform, id)
                - original_task: str - Input description

        Raises:
            ValueError: If response validation fails
            openai.error.OpenAIError: If API call fails after all retries
        """
        # Extract device information
        devices = self._extract_device_info(task_description)

        # Construct system prompt
        system_prompt = (
            "You are a UI automation expert that converts natural language "
            "task descriptions into precise UI automation steps. Each step "
            "should "
            "include:\n"
            "- A specific action (click, type, swipe, etc)\n"
            "- The target element or coordinates\n"
            "- The target platform (android/ios/web)\n"
            "- Any additional parameters needed\n"
            "- A clear description in the same language as the input\n\n"
            "Format each step as a JSON object with these fields:\n"
            "{\n"
            '    "action": string,\n'
            '    "target": string,\n'
            '    "platform": string,\n'
            '    "device_id": string or null,\n'
            '    "parameters": object,\n'
            '    "description": string,\n'
            '    "tool_name": string or null,\n'
            '    "tool_params": object or null\n'
            "}"
        )

        # Construct task prompt
        task_prompt = (
            f"""Please convert this UI automation task into specific steps:
            Task: {task_description}

            Required Platforms: {', '.join(d[0] for d in devices)}

            Output the steps as a JSON array of step objects."""
        )

        try:
            # Call OpenAI API with retry logic
            response = await self._call_openai_with_retry([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task_prompt}
            ])

            # Extract and parse response
            steps_json = response.choices[0].message.content
            try:
                steps_data = json.loads(steps_json)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                raise ValueError(f"Invalid JSON in LLM response: {e}")

            # Validate and process steps
            try:
                # Convert to UIStep objects and validate
                validated_steps = []
                for i, step in enumerate(steps_data):
                    try:
                        # Basic step validation
                        if not isinstance(step, dict):
                            raise ValueError(f"Step {i} is not a dictionary")
                        required = {"action", "target"}
                        if not required.issubset(step):
                            raise ValueError(
                                f"Step {i} missing required fields"
                            )

                        # Validate platform matches detected devices
                        if "platform" in step:
                            valid_platforms = [d[0] for d in devices]
                            if step["platform"] not in valid_platforms:
                                raise ValueError(
                                    f"Step {i} platform '{step['platform']}' "
                                    f"not in platforms {valid_platforms}"
                                )

                        # Validate device ID if present
                        if "device_id" in step and step["device_id"]:
                            device_ids = [d[1] for d in devices if d[1]]
                            if step["device_id"] not in device_ids:
                                raise ValueError(
                                    f"Step {i} device_id '{step['device_id']}'"
                                    f"not in devices {device_ids}"
                                )

                        # Convert to UIStep object
                        validated_step = UIStep(**step)
                        validated_steps.append(validated_step)

                    except Exception as e:
                        raise ValueError(f"Invalid step {i}: {str(e)}")

                # Verify we have at least one step
                if not validated_steps:
                    raise ValueError("No valid steps generated")

                # Check step ordering makes sense
                # For example, ensure login comes before actions requiring auth
                # Basic check - enhance with domain knowledge later
                auth_actions = {"send_message", "check_notifications"}
                logged_in = False
                for i, step in enumerate(validated_steps):
                    if step.action == "login":
                        logged_in = True
                    elif step.action in auth_actions and not logged_in:
                        raise ValueError(
                            f"Step {i} requires login but no prior login step"
                        )

                return {
                    "steps": [step.dict() for step in validated_steps],
                    "devices": devices,
                    "original_task": task_description
                }

            except Exception as e:
                logger.error(f"Failed to validate steps: {e}")
                raise ValueError(f"Invalid step format in LLM response: {e}")

        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_steps: {e}")
            raise
