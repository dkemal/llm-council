"""OpenAI direct API provider."""

import os
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """Provider for OpenAI API (GPT models)."""

    # Model name mappings: OpenRouter format -> OpenAI format
    MODEL_MAPPINGS = {
        "openai/gpt-4o": "gpt-4o",
        "openai/gpt-4o-mini": "gpt-4o-mini",
        "openai/gpt-4-turbo": "gpt-4-turbo",
        "openai/gpt-4": "gpt-4",
        "openai/gpt-3.5-turbo": "gpt-3.5-turbo",
        "openai/o1": "o1",
        "openai/o1-mini": "o1-mini",
        "openai/o1-preview": "o1-preview",
        "openai/gpt-5.1": "gpt-4o",  # Fallback for hypothetical models
    }

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None
        self.available = api_key is not None

    def supports_model(self, model: str) -> bool:
        """Check if this provider supports the given model."""
        if not self.available:
            return False
        # Support both OpenRouter format and direct format
        return model in self.MODEL_MAPPINGS or model.startswith("gpt-") or model.startswith("o1")

    def _normalize_model(self, model: str) -> str:
        """Convert OpenRouter model format to OpenAI format."""
        if model in self.MODEL_MAPPINGS:
            return self.MODEL_MAPPINGS[model]
        # Already in OpenAI format
        return model

    async def query(
        self,
        model: str,
        messages: List[Dict[str, str]],
        timeout: float = 120.0
    ) -> Optional[Dict[str, Any]]:
        """Query OpenAI API."""
        if not self.client:
            print("OpenAI API key not configured")
            return None

        try:
            normalized_model = self._normalize_model(model)

            response = await self.client.chat.completions.create(
                model=normalized_model,
                messages=messages,
                timeout=timeout
            )

            message = response.choices[0].message

            return {
                'content': message.content,
                'reasoning_details': None  # OpenAI doesn't expose reasoning details
            }

        except Exception as e:
            print(f"Error querying OpenAI model {model}: {e}")
            return None
