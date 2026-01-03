"""
Multi-provider LLM routing system.

Supports direct API calls to OpenAI, Anthropic, and Google,
with OpenRouter as fallback for unsupported models.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional

from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .google_provider import GoogleProvider
from .openrouter_provider import OpenRouterProvider


# Initialize providers (lazy loaded on first use)
_openai_provider: Optional[OpenAIProvider] = None
_anthropic_provider: Optional[AnthropicProvider] = None
_google_provider: Optional[GoogleProvider] = None
_openrouter_provider: Optional[OpenRouterProvider] = None


def _get_providers():
    """Lazy initialize providers."""
    global _openai_provider, _anthropic_provider, _google_provider, _openrouter_provider

    if _openai_provider is None:
        _openai_provider = OpenAIProvider()
    if _anthropic_provider is None:
        _anthropic_provider = AnthropicProvider()
    if _google_provider is None:
        _google_provider = GoogleProvider()
    if _openrouter_provider is None:
        _openrouter_provider = OpenRouterProvider()

    return _openai_provider, _anthropic_provider, _google_provider, _openrouter_provider


def get_llm_mode() -> str:
    """Get the LLM mode from environment."""
    return os.getenv("LLM_MODE", "openrouter").lower()


def _detect_provider(model: str):
    """Detect which provider to use for a model."""
    openai_prov, anthropic_prov, google_prov, openrouter_prov = _get_providers()

    mode = get_llm_mode()

    # In openrouter mode, always use OpenRouter
    if mode == "openrouter":
        return openrouter_prov

    # In direct mode, try to match provider based on model name
    if model.startswith("openai/") or model.startswith("gpt-") or model.startswith("o1"):
        if openai_prov.available:
            return openai_prov

    if model.startswith("anthropic/") or model.startswith("claude-"):
        if anthropic_prov.available:
            return anthropic_prov

    if model.startswith("google/") or model.startswith("gemini-"):
        if google_prov.available:
            return google_prov

    # Fallback to OpenRouter for unsupported models (x-ai/grok, etc.)
    if openrouter_prov.available:
        return openrouter_prov

    return None


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a model using the appropriate provider.

    Automatically routes to the correct provider based on model name
    and LLM_MODE configuration.

    Args:
        model: Model identifier (OpenRouter or direct format)
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds

    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    provider = _detect_provider(model)

    if provider is None:
        print(f"No available provider for model {model}")
        return None

    return await provider.query(model, messages, timeout)


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Args:
        models: List of model identifiers
        messages: List of message dicts to send to each model

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    # Create tasks for all models
    tasks = [query_model(model, messages) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}


def get_provider_status() -> Dict[str, bool]:
    """Get availability status of all providers."""
    openai_prov, anthropic_prov, google_prov, openrouter_prov = _get_providers()

    return {
        "openai": openai_prov.available,
        "anthropic": anthropic_prov.available,
        "google": google_prov.available,
        "openrouter": openrouter_prov.available,
        "mode": get_llm_mode(),
    }
