"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# ==============================================
# API Keys Configuration
# ==============================================

# Direct provider API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# OpenRouter API key (fallback)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# LLM Mode: "direct" or "openrouter"
LLM_MODE = os.getenv("LLM_MODE", "openrouter")

# ==============================================
# Council Configuration
# ==============================================

# Council members - list of model identifiers
# In "direct" mode: use provider-prefixed format (openai/gpt-4o, anthropic/claude-...)
# In "openrouter" mode: use OpenRouter model identifiers
COUNCIL_MODELS = [
    "openai/gpt-4o",                      # OpenAI GPT-4o
    "google/gemini-2.5-flash",            # Google Gemini 2.5 Flash
    "anthropic/claude-sonnet-4-20250514", # Anthropic Claude Sonnet 4
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "google/gemini-2.5-flash"

# Optional: Override from environment
_env_models = os.getenv("COUNCIL_MODELS")
if _env_models:
    COUNCIL_MODELS = [m.strip() for m in _env_models.split(",")]

_env_chairman = os.getenv("CHAIRMAN_MODEL")
if _env_chairman:
    CHAIRMAN_MODEL = _env_chairman.strip()

# ==============================================
# OpenRouter (legacy - kept for backward compatibility)
# ==============================================
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# ==============================================
# Storage
# ==============================================
DATA_DIR = "data/conversations"

# ==============================================
# Model Registry
# ==============================================

# Available models per provider
AVAILABLE_MODELS = {
    "openai": [
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "openai/o1",
        "openai/o1-mini",
    ],
    "anthropic": [
        "anthropic/claude-sonnet-4-20250514",
        "anthropic/claude-opus-4-20250514",
        "anthropic/claude-3.5-sonnet",
    ],
    "google": [
        "google/gemini-3-pro-preview",      # Gemini 3 Pro (latest, Jan 2026)
        "google/gemini-3-flash-preview",    # Gemini 3 Flash (fast, Jan 2026)
        "google/gemini-2.5-pro",            # Gemini 2.5 Pro
        "google/gemini-2.5-flash",          # Gemini 2.5 Flash
        "google/gemini-2.0-flash",          # Gemini 2.0 Flash
    ],
}

# Chairman-eligible models (powerful models only)
CHAIRMAN_ELIGIBLE_MODELS = [
    "openai/gpt-4o",
    "openai/o1",
    "anthropic/claude-sonnet-4-20250514",
    "anthropic/claude-opus-4-20250514",
    "google/gemini-3-pro-preview",          # Gemini 3 Pro
    "google/gemini-3-flash-preview",        # Gemini 3 Flash
    "google/gemini-2.5-pro",                # Gemini 2.5 Pro
    "google/gemini-2.5-flash",              # Gemini 2.5 Flash
]
