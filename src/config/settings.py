"""Configuration settings for the due diligence workflow."""

# Model name mappings - short names to GitHub Copilot model IDs
# Run `await client.list_models()` to see all models available on your subscription.
MODEL_MAPPING = {
    "haiku": "gpt-4.1-mini",      # fast / low-cost
    "sonnet": "claude-sonnet-4.5",  # balanced
    "opus": "gpt-5",               # highest capability
}


def get_model_id(model_name: str) -> str:
    """Get the full model ID from a short name.
    
    Args:
        model_name: Short name like 'haiku', 'sonnet', 'opus' or full ID
    
    Returns:
        Full model ID string
    """
    return MODEL_MAPPING.get(model_name, model_name)