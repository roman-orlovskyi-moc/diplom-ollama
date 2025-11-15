"""
Defense mechanisms base class and exports
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class DefenseBase(ABC):
    """Base class for all defense mechanisms"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self.enabled = True

    @abstractmethod
    def protect_input(self, user_input: str, system_prompt: str) -> Dict[str, str]:
        """
        Apply defense to input before sending to LLM

        Args:
            user_input: The user's message
            system_prompt: The system prompt

        Returns:
            Dict with 'user_input' and 'system_prompt' (potentially modified)
        """
        pass

    @abstractmethod
    def protect_output(self, output: str, context: Dict[str, Any]) -> str:
        """
        Apply defense to LLM output before returning

        Args:
            output: The LLM's response
            context: Additional context (original input, system_prompt, etc.)

        Returns:
            Protected output string
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Return defense mechanism metadata"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'config': self.config,
            'description': self.__doc__ or 'No description available'
        }

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.name}(enabled={self.enabled})"