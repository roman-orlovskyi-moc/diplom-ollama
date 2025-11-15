"""
Input Sanitization Defense
Filters and cleans user input to remove suspicious patterns
"""
import re
from typing import Dict, Any
from src.defenses import DefenseBase


class InputSanitizer(DefenseBase):
    """Remove or escape dangerous patterns from input"""

    def __init__(self, config=None):
        super().__init__(config)
        self.blocklist_patterns = self.config.get('blocklist_patterns', [
            r'ignore\s+(all\s+)?previous\s+instructions?',
            r'disregard\s+(all\s+)?previous',
            r'forget\s+(everything|all)',
            r'system\s*:',
            r'###\s*end',
            r'you\s+are\s+now',
            r'pretend\s+to\s+be',
            r'new\s+instructions?',
            r'override',
            r'admin\s+mode',
            r'developer\s+mode',
            r'DAN',
            r'do\s+anything\s+now',
        ])
        self.max_length = self.config.get('max_length', 2000)

    def protect_input(self, user_input: str, system_prompt: str) -> Dict[str, str]:
        """
        Sanitize user input by removing dangerous patterns

        Args:
            user_input: The user's message
            system_prompt: The system prompt

        Returns:
            Dict with sanitized input and original system prompt
        """
        sanitized = user_input

        # Remove blocklisted patterns
        for pattern in self.blocklist_patterns:
            sanitized = re.sub(pattern, '[FILTERED]', sanitized, flags=re.IGNORECASE)

        # Escape special characters that might be used for injection
        sanitized = sanitized.replace('###', '')

        # Remove excessive newlines (potential formatting abuse)
        sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)

        # Limit length to prevent overflow attacks
        if len(sanitized) > self.max_length:
            sanitized = sanitized[:self.max_length] + '... [TRUNCATED]'

        return {
            'user_input': sanitized,
            'system_prompt': system_prompt
        }

    def protect_output(self, output: str, context: Dict[str, Any]) -> str:
        """
        No output filtering for this defense

        Args:
            output: The LLM's response
            context: Additional context

        Returns:
            Unmodified output
        """
        return output