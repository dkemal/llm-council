"""Google Gemini direct API provider."""

import os
from typing import List, Dict, Any, Optional
from .base import BaseLLMProvider

# Import conditionally to handle missing dependency gracefully
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GoogleProvider(BaseLLMProvider):
    """Provider for Google Gemini API."""

    # Model name mappings: OpenRouter format -> Gemini format
    MODEL_MAPPINGS = {
        "google/gemini-pro": "gemini-1.5-pro",
        "google/gemini-1.5-pro": "gemini-1.5-pro",
        "google/gemini-1.5-flash": "gemini-1.5-flash",
        "google/gemini-2.0-flash": "gemini-2.0-flash-exp",
        "google/gemini-3-pro-preview": "gemini-1.5-pro",  # Hypothetical -> latest stable
    }

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.available = self.api_key is not None and GENAI_AVAILABLE

        if self.available:
            genai.configure(api_key=self.api_key)

    def supports_model(self, model: str) -> bool:
        """Check if this provider supports the given model."""
        if not self.available:
            return False
        return model in self.MODEL_MAPPINGS or model.startswith("gemini-")

    def _normalize_model(self, model: str) -> str:
        """Convert OpenRouter model format to Gemini format."""
        if model in self.MODEL_MAPPINGS:
            return self.MODEL_MAPPINGS[model]
        # Remove google/ prefix if present
        if model.startswith("google/"):
            return model[7:]
        return model

    async def query(
        self,
        model: str,
        messages: List[Dict[str, str]],
        timeout: float = 120.0
    ) -> Optional[Dict[str, Any]]:
        """Query Google Gemini API."""
        if not self.available:
            print("Google API key not configured or google-generativeai not installed")
            return None

        try:
            normalized_model = self._normalize_model(model)

            # Create model instance
            gemini_model = genai.GenerativeModel(normalized_model)

            # Convert messages to Gemini format
            # Gemini uses 'user' and 'model' roles
            gemini_history = []
            system_instruction = None

            for msg in messages:
                role = msg["role"]
                content = msg["content"]

                if role == "system":
                    system_instruction = content
                elif role == "user":
                    gemini_history.append({"role": "user", "parts": [content]})
                elif role == "assistant":
                    gemini_history.append({"role": "model", "parts": [content]})

            # If we have a system instruction, prepend to first user message
            if system_instruction and gemini_history:
                first_user_content = gemini_history[0]["parts"][0]
                gemini_history[0]["parts"][0] = f"{system_instruction}\n\n{first_user_content}"

            # Start chat and get response
            chat = gemini_model.start_chat(history=gemini_history[:-1] if len(gemini_history) > 1 else [])

            # Send last message
            last_message = gemini_history[-1]["parts"][0] if gemini_history else ""
            response = await chat.send_message_async(last_message)

            return {
                'content': response.text,
                'reasoning_details': None
            }

        except Exception as e:
            print(f"Error querying Google model {model}: {e}")
            return None
