"""
LLM Client abstraction layer
Provides unified interface for different LLM providers
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum
import time

from config.settings import (
    OLLAMA_BASE_URL,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_ANTHROPIC_MODEL
)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMClient(ABC):
    """Abstract base class for LLM clients"""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion from LLM

        Args:
            prompt: User prompt/message
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters

        Returns:
            {
                'response': str,
                'model': str,
                'tokens_used': int,
                'cost': float,
                'latency_ms': int
            }
        """
        pass


class OllamaClient(LLMClient):
    """Client for local Ollama LLM"""

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = DEFAULT_OLLAMA_MODEL):
        self.base_url = base_url.rstrip('/')
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using Ollama"""
        import requests

        start_time = time.time()

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            data = response.json()

            tokens_used = data.get('eval_count', 0)
            latency_ms = int((time.time() - start_time) * 1000)
            cost = 0.0

            response_content = data.get('response', '')

            print(f"[Ollama] Model: {self.model}")
            print(f"[Ollama] Response content: {response_content}")
            print(f"[Ollama] Tokens used: {tokens_used}")
            print(f"[Ollama] Cost: {cost}")
            print(f"[Ollama] Latency (ms): {latency_ms}")
            print(f"{'='*80}")

            return {
                'response': response_content,
                'model': self.model,
                'tokens_used': tokens_used,
                'cost': cost,
                'latency_ms': latency_ms
            }

        except requests.exceptions.RequestException as e:
            return {
                'response': f"Error: {str(e)}",
                'model': self.model,
                'tokens_used': 0,
                'cost': 0.0,
                'latency_ms': int((time.time() - start_time) * 1000),
                'error': str(e)
            }


class OpenAIClient(LLMClient):
    """Client for OpenAI API"""

    def __init__(self, api_key: str, model: str = DEFAULT_OPENAI_MODEL):
        self.api_key = api_key
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using OpenAI"""
        try:
            from openai import OpenAI
        except ImportError:
            return {
                'response': "Error: openai package not installed",
                'model': self.model,
                'tokens_used': 0,
                'cost': 0.0,
                'latency_ms': 0,
                'error': 'openai package not installed'
            }

        start_time = time.time()

        try:
            client = OpenAI(api_key=self.api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=max_tokens,
                # temperature=temperature # ignore temperature for now
            )

            latency_ms = int((time.time() - start_time) * 1000)
            tokens_used = response.usage.total_tokens

            response_content = response.choices[0].message.content

            if 'gpt-5-nano' in self.model:
                cost_per_1k_tokens = 0.005
            else:
                cost_per_1k_tokens = 0.002
            cost = (tokens_used / 1000) * cost_per_1k_tokens

            print(f"[OpenAI] Model: {self.model}")
            print(f"[OpenAI] Response content: {response_content}")
            print(f"[OpenAI] Tokens used: {tokens_used}")
            print(f"[OpenAI] Cost: {cost}")
            print(f"[OpenAI] Latency (ms): {latency_ms}")
            print(f"{'='*80}")

            return {
                'response': response_content or "",
                'model': self.model,
                'tokens_used': tokens_used,
                'cost': cost,
                'latency_ms': latency_ms
            }

        except Exception as e:
            return {
                'response': f"Error: {str(e)}",
                'model': self.model,
                'tokens_used': 0,
                'cost': 0.0,
                'latency_ms': int((time.time() - start_time) * 1000),
                'error': str(e)
            }


class AnthropicClient(LLMClient):
    """Client for Anthropic Claude API"""

    def __init__(self, api_key: str, model: str = DEFAULT_ANTHROPIC_MODEL):
        self.api_key = api_key
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using Anthropic"""
        try:
            from anthropic import Anthropic
        except ImportError:
            return {
                'response': "Error: anthropic package not installed",
                'model': self.model,
                'tokens_used': 0,
                'cost': 0.0,
                'latency_ms': 0,
                'error': 'anthropic package not installed'
            }

        start_time = time.time()

        try:
            client = Anthropic(api_key=self.api_key)

            kwargs_api = {'max_tokens': max_tokens, 'temperature': temperature}
            if system_prompt:
                kwargs_api['system'] = system_prompt

            response = client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs_api
            )

            latency_ms = int((time.time() - start_time) * 1000)
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            response_content = response.content[0].text

            cost_per_1k_input = 0.0001
            cost_per_1k_output = 0.0005
            cost = (response.usage.input_tokens / 1000) * cost_per_1k_input + \
                   (response.usage.output_tokens / 1000) * cost_per_1k_output

            print(f"[Anthropic] Model: {self.model}")
            print(f"[Anthropic] Response content: {response_content}")
            print(f"[Anthropic] Tokens used: {tokens_used}")
            print(f"[Anthropic] Cost: {cost}")
            print(f"[Anthropic] Latency (ms): {latency_ms}")
            print(f"{'='*80}")

            return {
                'response': response_content or "",
                'model': self.model,
                'tokens_used': tokens_used,
                'cost': cost,
                'latency_ms': latency_ms
            }

        except Exception as e:
            return {
                'response': f"Error: {str(e)}",
                'model': self.model,
                'tokens_used': 0,
                'cost': 0.0,
                'latency_ms': int((time.time() - start_time) * 1000),
                'error': str(e)
            }


class LLMClientFactory:
    """Factory for creating LLM client instances"""

    @staticmethod
    def create(provider: LLMProvider, **config) -> LLMClient:
        """
        Create LLM client based on provider

        Args:
            provider: LLM provider enum
            **config: Provider-specific configuration

        Returns:
            LLMClient instance
        """
        if provider == LLMProvider.OLLAMA:
            return OllamaClient(
                base_url=config.get('base_url', OLLAMA_BASE_URL),
                model=config.get('model', DEFAULT_OLLAMA_MODEL)
            )
        elif provider == LLMProvider.OPENAI:
            if 'api_key' not in config:
                raise ValueError("OpenAI requires api_key in config")
            return OpenAIClient(
                api_key=config['api_key'],
                model=config.get('model', DEFAULT_OPENAI_MODEL)
            )
        elif provider == LLMProvider.ANTHROPIC:
            if 'api_key' not in config:
                raise ValueError("Anthropic requires api_key in config")
            return AnthropicClient(
                api_key=config['api_key'],
                model=config.get('model', DEFAULT_ANTHROPIC_MODEL)
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    @staticmethod
    def create_from_env() -> LLMClient:
        """Create LLM client from environment variables"""
        from config.settings import (
            LLM_PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL,
            OPENAI_API_KEY, OPENAI_MODEL,
            ANTHROPIC_API_KEY, ANTHROPIC_MODEL
        )

        provider = LLMProvider(LLM_PROVIDER)

        if provider == LLMProvider.OLLAMA:
            return OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
        elif provider == LLMProvider.OPENAI:
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in environment")
            return OpenAIClient(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
        elif provider == LLMProvider.ANTHROPIC:
            if not ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")
            return AnthropicClient(api_key=ANTHROPIC_API_KEY, model=ANTHROPIC_MODEL)