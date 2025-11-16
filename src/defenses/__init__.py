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


# Import all defense implementations
from src.defenses.input_sanitizer import InputSanitizer
from src.defenses.prompt_template import PromptTemplate
from src.defenses.output_filter import OutputFilter
from src.defenses.context_isolation import ContextIsolation
from src.defenses.dual_llm import DualLLM
from src.defenses.instruction_hierarchy import InstructionHierarchy

# Try to import ML-based defenses (optional dependencies)
try:
    from src.defenses.perplexity_filter import PerplexityFilter
    PERPLEXITY_AVAILABLE = True
except ImportError:
    PERPLEXITY_AVAILABLE = False
    PerplexityFilter = None

try:
    from src.defenses.semantic_similarity import SemanticSimilarity
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    SemanticSimilarity = None

__all__ = [
    'DefenseBase',
    'InputSanitizer',
    'PromptTemplate',
    'OutputFilter',
    'ContextIsolation',
    'DualLLM',
    'InstructionHierarchy',
    'PerplexityFilter',
    'SemanticSimilarity',
    'PERPLEXITY_AVAILABLE',
    'SEMANTIC_AVAILABLE'
]