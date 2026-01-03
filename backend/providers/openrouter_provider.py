"""OpenRouter API provider (fallback for unsupported models)."""

import os
import httpx
from typing import List, Dict, Any, Optional
from .base import BaseLLMProvider


class OpenRouterProvider(BaseLLMProvider):
    """Provider for OpenRouter API (supports all models as fallback)."""

    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.available = self.api_key is not None

    def supports_model(self, model: str) -> bool:
        """OpenRouter supports all models as fallback."""
        return self.available

    async def query(
        self,
        model: str,
        messages: List[Dict[str, str]],
        timeout: float = 120.0
    ) -> Optional[Dict[str, Any]]:
        """Query OpenRouter API."""
        if not self.api_key:
            print("OpenRouter API key not configured")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    self.API_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                data = response.json()
                message = data['choices'][0]['message']

                return {
                    'content': message.get('content'),
                    'reasoning_details': message.get('reasoning_details')
                }

        except Exception as e:
            print(f"Error querying OpenRouter model {model}: {e}")
            return None
