"""
Perplexity Filter Defense

This defense uses language model perplexity to detect unusual or obfuscated inputs.
High perplexity indicates text that doesn't follow natural language patterns,
which often signals encoding, obfuscation, or adversarial attacks.

Technique: ML-based Detection
Approach: Uses a small pre-trained language model to calculate perplexity scores.
          Blocks inputs with unusually high perplexity as potential attacks.
"""
from typing import Dict, Any, Optional
from src.defenses import DefenseBase
from config.settings import DEFAULT_PERPLEXITY_MODEL

# Lazy import - only import torch when actually needed
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class PerplexityFilter(DefenseBase):
    """
    Detects and blocks obfuscated or encoded attacks using perplexity scoring.

    Perplexity measures how "surprised" a language model is by text.
    - Low perplexity (~10-100): Natural, expected text
    - Medium perplexity (~100-200): Somewhat unusual text
    - High perplexity (>200): Very unusual, likely encoded/obfuscated

    This defense is particularly effective against:
    - Base64 and other encoding schemes
    - ROT13, Caesar ciphers
    - Random character sequences
    - Unicode obfuscation
    - Leetspeak and character substitution
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

        # Configuration
        self.threshold = config.get('threshold', 150) if config else 150
        self.model_name = config.get('model_name', DEFAULT_PERPLEXITY_MODEL) if config else DEFAULT_PERPLEXITY_MODEL
        self.max_length = config.get('max_length', 512) if config else 512
        self.block_message = config.get('block_message',
            '[BLOCKED: Input appears to be encoded or obfuscated]') if config else \
            '[BLOCKED: Input appears to be encoded or obfuscated]'

        # Lazy loading - only load model when first used
        self.model = None
        self.tokenizer = None
        self._model_loaded = False

    def _load_model(self):
        """Lazy load the language model for perplexity calculation"""
        if self._model_loaded:
            return

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            print(f"Loading {self.model_name} for perplexity calculation...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.model.eval()  # Set to evaluation mode

            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self._model_loaded = True
            print(f"✓ {self.model_name} loaded successfully")

        except ImportError:
            print("\n" + "="*70)
            print("ERROR: transformers library not installed!")
            print("To use PerplexityFilter, install required packages:")
            print("  pip install transformers torch")
            print("="*70 + "\n")
            self.enabled = False
            raise

        except Exception as e:
            print(f"\n" + "="*70)
            print(f"ERROR loading {self.model_name}: {e}")
            print("Perplexity filter will be disabled.")
            print("="*70 + "\n")
            self.enabled = False

    def _calculate_perplexity(self, text: str) -> float:
        """
        Calculate perplexity score for input text

        Args:
            text: Input text to evaluate

        Returns:
            Perplexity score (float)
        """
        if not self.enabled:
            return 0.0

        # Load model if needed
        if not self._model_loaded:
            self._load_model()

        if not self._model_loaded:  # Still not loaded - error occurred
            return 0.0

        try:
            # Tokenize input
            encodings = self.tokenizer(
                text,
                max_length=self.max_length,
                truncation=True,
                return_tensors='pt'
            )

            # Calculate perplexity
            with torch.no_grad():
                outputs = self.model(**encodings, labels=encodings['input_ids'])
                loss = outputs.loss

            perplexity = torch.exp(loss).item()
            return perplexity

        except Exception as e:
            print(f"Error calculating perplexity: {e}")
            return 0.0  # Default to allowing if error

    def protect_input(self, user_input: str, system_prompt: str) -> Dict[str, str]:
        """
        Check input perplexity and block if too high

        Args:
            user_input: The user's message
            system_prompt: The system prompt

        Returns:
            Dict with user_input and system_prompt (user_input blocked if high perplexity)
        """
        if not self.enabled:
            return {'user_input': user_input, 'system_prompt': system_prompt}

        # Skip very short inputs (perplexity unreliable)
        if len(user_input.strip()) < 10:
            return {'user_input': user_input, 'system_prompt': system_prompt}

        # Calculate perplexity
        perplexity = self._calculate_perplexity(user_input)

        # Check against threshold
        if perplexity > self.threshold:
            # High perplexity - likely attack
            return {
                'user_input': f"{self.block_message} (perplexity: {perplexity:.1f})",
                'system_prompt': system_prompt
            }

        # Normal perplexity - allow
        return {
            'user_input': user_input,
            'system_prompt': system_prompt
        }

    def protect_output(self, output: str, context: Dict[str, Any]) -> str:
        """
        No output protection needed for perplexity filter

        Args:
            output: The LLM's response
            context: Additional context

        Returns:
            Unmodified output
        """
        return output

    def get_perplexity_score(self, text: str) -> Optional[float]:
        """
        Public method to get perplexity score for analysis

        Args:
            text: Text to evaluate

        Returns:
            Perplexity score or None if disabled
        """
        if not self.enabled:
            return None
        return self._calculate_perplexity(text)

    def get_metadata(self) -> Dict[str, Any]:
        """Return defense metadata"""
        return {
            'name': self.name,
            'type': 'ml_based_detection',
            'approach': 'Perplexity-based anomaly detection',
            'enabled': self.enabled,
            'config': {
                'threshold': self.threshold,
                'model_name': self.model_name,
                'max_length': self.max_length
            },
            'description': 'Detects encoded/obfuscated inputs using language model perplexity',
            'strengths': [
                'Catches encoding attacks (Base64, ROT13, etc.)',
                'Detects character substitution and leetspeak',
                'Language-agnostic detection',
                'No training required (uses pre-trained model)'
            ],
            'weaknesses': [
                'Requires model inference (adds latency)',
                'May flag legitimate technical content',
                'Threshold tuning needed for optimal performance',
                'Less effective on natural language attacks'
            ],
            'effective_against': [
                'Base64 encoding',
                'ROT13 and Caesar ciphers',
                'Unicode obfuscation',
                'Leetspeak',
                'Random character injection',
                'ASCII art attacks'
            ]
        }

    def __str__(self) -> str:
        return "PerplexityFilter"

    def __repr__(self) -> str:
        return f"PerplexityFilter(threshold={self.threshold}, model={self.model_name}, enabled={self.enabled})"