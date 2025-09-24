"""
Model ID Mapping for AI Clients
Handles conversion between display names and API model IDs
"""

# Model ID mapping from display names to API format
MODEL_ID_MAPPING = {
    # xAI Grok models
    "xAI: Grok Code Fast 1": "x-ai/grok-code-fast-1",
    "xAI: Grok 4 Fast": "x-ai/grok-4-fast",
    "xAI: Grok 4 Fast (free)": "x-ai/grok-4-fast:free",
    "xAI: Grok 4": "x-ai/grok-4",
    "xAI: Grok 3 Mini": "x-ai/grok-3-mini",
    "xAI: Grok 3": "x-ai/grok-3",
    "xAI: Grok 3 Mini Beta": "x-ai/grok-3-mini-beta",
    "xAI: Grok 3 Beta": "x-ai/grok-3-beta",
    # Common alternatives
    "Grok Code Fast 1": "x-ai/grok-code-fast-1",
    "Grok 4 Fast": "x-ai/grok-4-fast",
    "Grok 4": "x-ai/grok-4",
    "Grok 3": "x-ai/grok-3",
    # OpenAI models (common display names)
    "GPT-4": "openai/gpt-4",
    "GPT-4 Turbo": "openai/gpt-4-turbo",
    "GPT-3.5 Turbo": "openai/gpt-3.5-turbo",
    # Anthropic models
    "Claude 3 Haiku": "anthropic/claude-3-haiku",
    "Claude 3 Sonnet": "anthropic/claude-3-sonnet",
    "Claude 3 Opus": "anthropic/claude-3-opus",
    # Google models
    "Gemini Pro": "google/gemini-pro",
    "Gemini 1.5 Pro": "google/gemini-1.5-pro",
}


def normalize_model_id(model_id: str) -> str:
    """
    Convert display name or invalid format to proper API model ID

    Args:
        model_id: The model ID to normalize (could be display name or API format)

    Returns:
        Properly formatted API model ID
    """
    if not model_id:
        return "anthropic/claude-3-haiku"  # Safe fallback

    # Remove extra whitespace
    model_id = model_id.strip()

    # Check direct mapping first
    if model_id in MODEL_ID_MAPPING:
        return MODEL_ID_MAPPING[model_id]

    # If it's already in API format (contains slash), return as-is
    if "/" in model_id:
        return model_id

    # Try fuzzy matching for common cases
    model_lower = model_id.lower()

    # xAI Grok fuzzy matching
    if "grok" in model_lower and "code" in model_lower and "fast" in model_lower:
        return "x-ai/grok-code-fast-1"
    elif "grok" in model_lower and "4" in model_lower and "fast" in model_lower:
        return "x-ai/grok-4-fast"
    elif "grok" in model_lower and "4" in model_lower:
        return "x-ai/grok-4"
    elif "grok" in model_lower and "3" in model_lower:
        return "x-ai/grok-3"

    # GPT fuzzy matching
    elif "gpt-4" in model_lower or "gpt4" in model_lower:
        if "turbo" in model_lower:
            return "openai/gpt-4-turbo"
        return "openai/gpt-4"
    elif "gpt-3.5" in model_lower or "gpt3.5" in model_lower:
        return "openai/gpt-3.5-turbo"

    # Claude fuzzy matching
    elif "claude" in model_lower:
        if "haiku" in model_lower:
            return "anthropic/claude-3-haiku"
        elif "sonnet" in model_lower:
            return "anthropic/claude-3-sonnet"
        elif "opus" in model_lower:
            return "anthropic/claude-3-opus"
        return "anthropic/claude-3-haiku"  # Default Claude

    # If no match found, return a safe fallback
    return "anthropic/claude-3-haiku"


def get_model_display_name(api_model_id: str) -> str:
    """
    Convert API model ID back to display name

    Args:
        api_model_id: The API model ID

    Returns:
        Human-readable display name
    """
    # Reverse lookup in mapping
    for display_name, api_id in MODEL_ID_MAPPING.items():
        if api_id == api_model_id:
            return display_name

    # If not found, return the API ID as-is
    return api_model_id
