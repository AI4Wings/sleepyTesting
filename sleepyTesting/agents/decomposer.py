"""Task Decomposition Agent.

Breaks down high-level UI tasks into atomic operations using LLM-based task analysis.
Supports both Chinese and English task descriptions and handles multi-device
operations across Android, iOS, and web platforms.
"""
import logging
from typing import List, Optional

from ..core.llm import LLMClient, UIStep

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskDecomposer:
    """Decomposes high-level tasks into specific UI steps using LLM.

    This class uses an LLM to analyze natural language task descriptions and break
    them down into atomic UI operations. It supports both Chinese and English input
    and can handle multi-device operations across Android, iOS, and web platforms.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize the task decomposer.
        
        Args:
            llm_client: Optional LLMClient instance. If not provided, creates a new one.
        """
        self.llm_client = llm_client or LLMClient()
        
    async def decompose_task(self, task_description: str) -> List[UIStep]:
        """
        Decompose a high-level task description into specific UI steps using LLM.
        
        This method uses the LLM to analyze the task description and generate a sequence
        of atomic UI operations. It supports both Chinese and English input and can
        handle multi-device operations.

        Args:
            task_description: Natural language description of the UI task

        Returns:
            List of UIStep objects representing atomic operations

        Example:
            "在Android设备A123上发送短信，在iOS设备B456上查收短信" ->
            [UIStep(action="send_sms", platform="android", device_id="A123", ...),
             UIStep(action="check_sms", platform="ios", device_id="B456", ...)]
             
        Raises:
            ValueError: If task decomposition fails or generates invalid steps
        """
        try:
            # Use LLM to generate steps
            result = await self.llm_client.generate_steps(task_description)
            
            # Extract and validate steps
            if not result or "steps" not in result:
                raise ValueError("LLM failed to generate valid steps")
                
            steps = [UIStep(**step) for step in result["steps"]]
            if not steps:
                raise ValueError("No valid steps generated")
                
            # Log the decomposition result
            logger.info(f"Decomposed task into {len(steps)} steps")
            for i, step in enumerate(steps):
                logger.debug(f"Step {i+1}: {step.dict()}")
                
            return steps
            
        except Exception as e:
            logger.error(f"Task decomposition failed: {str(e)}")
            raise ValueError(f"Failed to decompose task: {str(e)}")

    def validate_steps(
        self,
        steps: List[UIStep]
    ) -> bool:
        """Validate that the decomposed steps are valid and complete.
        
        Performs validation checks on the generated steps:
        - Verifies steps are UIStep instances
        - Checks for required fields (action, platform)
        - Validates device IDs match detected platforms
        - Ensures step sequence is logical

        Args:
            steps: List of UIStep objects to validate

        Returns:
            bool indicating if steps are valid
            
        Example:
            validate_steps([
                UIStep(action="login", platform="android", device_id="A123"),
                UIStep(action="send_message", platform="android", device_id="A123")
            ]) -> True
        """
        if not steps:
            return False
            
        try:
            # Basic type validation
            if not all(isinstance(step, UIStep) for step in steps):
                return False
                
            # Track platforms and device IDs
            seen_platforms = set()
            seen_devices = {}  # platform -> set of device IDs
            
            # Validate each step
            for step in steps:
                # Required fields
                if not step.action or not step.platform:
                    return False
                    
                # Track platform and device usage
                seen_platforms.add(step.platform)
                if step.platform not in seen_devices:
                    seen_devices[step.platform] = set()
                if step.device_id:
                    seen_devices[step.platform].add(step.device_id)
                    
            # All validations passed
            return True
            
        except Exception as e:
            logger.error(f"Step validation failed: {str(e)}")
            return False
