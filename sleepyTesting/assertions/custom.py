"""
Custom assertions for UI testing
"""
from typing import Callable
from .assertions import AssertionType, AssertionResult


class CustomAssertion:
    """Handles custom assertions"""

    @staticmethod
    def create(
            check_function: Callable[..., bool],
            error_message: str,
            **kwargs
    ) -> AssertionResult:
        """
        Create a custom assertion

        Args:
            check_function: Function that performs the check
            error_message: Message to show on failure
            **kwargs: Additional arguments for check_function

        Returns:
            AssertionResult object
        """
        try:
            passed = check_function(**kwargs)
            return AssertionResult(
                type=AssertionType.CUSTOM,
                passed=passed,
                message=(
                    error_message
                    if not passed
                    else "Custom assertion passed"
                ),
                actual_value=kwargs.get('actual'),
                expected_value=kwargs.get('expected')
            )
        except Exception as e:
            return AssertionResult(
                type=AssertionType.CUSTOM,
                passed=False,
                message=f"Custom assertion failed with error: {str(e)}",
                suggestion="Check the custom assertion implementation"
            )
