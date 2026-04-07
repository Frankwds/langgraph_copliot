"""Configuration settings for the due diligence workflow."""

# Model name mappings - short names to GitHub Copilot model IDs
# Run `await client.list_models()` to see all models available on your subscription.
MODEL_MAPPING = {
    # Short aliases
    "haiku": "claude-haiku-4.5",    # fast / low-cost
    "sonnet": "claude-sonnet-4.6",  # balanced
    "opus": "claude-opus-4.6",      # highest capability

    # All available GPT models
    "gpt-4.1":         "gpt-4.1",
    "gpt-5-mini":      "gpt-5-mini",
    "gpt-5.1":         "gpt-5.1",
    "gpt-5.2":         "gpt-5.2",
    "gpt-5.2-codex":   "gpt-5.2-codex",
    "gpt-5.3-codex":   "gpt-5.3-codex",
    "gpt-5.4":         "gpt-5.4",
}


def get_model_id(model_name: str) -> str:
    """Get the full model ID from a short name.
    
    Args:
        model_name: Short name like 'haiku', 'sonnet', 'opus' or full ID
    
    Returns:
        Full model ID string
    """
    return MODEL_MAPPING.get(model_name, model_name)