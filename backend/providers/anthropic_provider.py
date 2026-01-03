"""Anthropic direct API provider."""

import os
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic
from .base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Provider for Anthropic API (Claude models)."""

    # Model name mappings: OpenRouter format -> Anthropic format
    MODEL_MAPPINGS = {
        "anthropic/claude-3.5-sonnet": "claude-sonnet-4-20250514",
        "anthropic/claude-3-opus": "claude-3-opus-20240229",
        "anthropic/claude-3-sonnet": "claude-3-sonnet-20240229",
        "anthropic/claude-3-haiku": "claude-3-haiku-20240307",
        "anthropic/claude-sonnet-4.5": "claude-sonnet-4-20250514",  # Hypothetical -> latest
        "anthropic/claude-3.5-sonnet-20241022": "claude-3-5-sonnet-20241022",
    }

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = AsyncAnthropic(api_key=api_key) if api_key else None
        self.available = api_key is not None

    def supports_model(self, model: str) -> bool:
        """Check if this provider supports the given model."""
        if not self.available:
            return False
        return model in self.MODEL_MAPPINGS or model.startswith("claude-")

    def _normalize_model(self, model: str) -> str:
        """Convert OpenRouter model format to Anthropic format."""
        if model in self.MODEL_MAPPINGS:
            return self.MODEL_MAPPINGS[model]
        # Remove anthropic/ prefix if present
        if model.startswith("anthropic/"):
            return model[10:]
        return model

    async def query(
        self,
        model: str,
        messages: List[Dict[str, str]],
        timeout: float = 120.0
    ) -> Optional[Dict[str, Any]]:
        """Query Anthropic API."""
        if not self.client:
            print("Anthropic API key not configured")
            return None

        try:
            normalized_model = self._normalize_model(model)

            # Anthropic requires separating system message
            system_message = None
            user_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)

            # Build request
            request_kwargs = {
                "model": normalized_model,
                "max_tokens": 4096,
                "messages": user_messages,
            }

            if system_message:
                request_kwargs["system"] = system_message

            response = await self.client.messages.create(**request_kwargs)

            # Extract content from response
            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

            return {
                'content': content,
                'reasoning_details': None
            }

        except Exception as e:
            print(f"Error querying Anthropic model {model}: {e}")
            return None
