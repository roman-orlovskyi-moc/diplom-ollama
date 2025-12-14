"""
Output Filtering Defense
Scans LLM output for leaked system prompts or inappropriate content
"""
import re
from typing import Dict, Any
from src.defenses import DefenseBase


class OutputFilter(DefenseBase):
    """Filter LLM output for sensitive content"""

    def __init__(self, config=None):
        super().__init__(config)
        self.forbidden_patterns = self.config.get('forbidden_patterns', [
            r'system prompt',
            r'system instructions?',
            r'you are (a|an) .+? that',
            r'my instructions are',
            r'I was instructed to',
            r'API[_\s]?KEY',
            r'PASSWORD',
            r'SECRET',
        ])
        self.overlap_threshold = self.config.get('overlap_threshold', 0.3)
        self.block_message = self.config.get(
            'block_message',
            "I'm sorry, I cannot provide that information."
        )

    def protect_input(self, user_input: str, system_prompt: str) -> Dict[str, str]:
        """
        No input protection for this defense

        Args:
            user_input: The user's message
            system_prompt: The system prompt

        Returns:
            Unmodified inputs
        """
        return {
            'user_input': user_input,
            'system_prompt': system_prompt
        }

    def protect_output(self, output: str, context: Dict[str, Any]) -> str:
        """
        Filter output for sensitive information

        Args:
            output: The LLM's response
            context: Additional context including system_prompt

        Returns:
            Filtered output or block message
        """

        for pattern in self.forbidden_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return self.block_message

        system_prompt = context.get('system_prompt', '')
        if system_prompt and len(system_prompt) > 50:
            overlap = self._calculate_overlap(output, system_prompt)
            if overlap > self.overlap_threshold:
                return self.block_message

        if re.search(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', output):
            return self.block_message

        if re.search(r'\b(sk|pk)[-_][a-zA-Z0-9]{20,}\b', output):
            return self.block_message

        return output

    def _calculate_overlap(self, text1: str, text2: str) -> float:
        """
        Calculate word overlap percentage between two texts

        Args:
            text1: First text
            text2: Second text (reference)

        Returns:
            Overlap ratio (0.0 to 1.0)
        """
        # Tokenize into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words2:
            return 0.0

        intersection = words1.intersection(words2)
        return len(intersection) / len(words2)