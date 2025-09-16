"""
Utility functions for Botanist.
"""

import re

# Allow only letters, digits, spaces, and common punctuation
SAFE_DESC_RE = re.compile(r"[^a-zA-Z0-9 \t\.,;:!?()\[\]\-_\"'/\\]+")


def sanitize_description(description):
    """
    Sanitize user description input for security and data integrity.
    
    Args:
        description (str): Raw user input description
        
    Returns:
        str: Sanitized description
    """
    if not isinstance(description, str) or not description:
        return "None provided."

    # Remove leading/trailing whitespace
    description = description.strip()

    # Return default if empty after stripping
    if not description:
        return "None provided."

    # First, remove dangerous patterns (before stripping symbols like < >)
    dangerous_patterns = [
        r"<script.*?</script>",          # HTML script blocks
        r"script\s*.*?/\s*script",      # bracketless 'script.../script'
        r"javascript\s*:",
        r"data\s*:",
        r"vbscript\s*:",
        r"on\w+\s*=",                   # inline event handlers
    ]
    for pattern in dangerous_patterns:
        description = re.sub(pattern, "", description, flags=re.IGNORECASE | re.DOTALL)

    # Remove potentially dangerous characters and control characters
    # Keep alphanumeric, spaces, and common punctuation
    description = SAFE_DESC_RE.sub('', description)

    # Collapse multiple spaces into single space
    description = re.sub(r"\s+", " ", description)

    # Limit length to prevent extremely long descriptions
    max_length = 200
    if len(description) > max_length:
        description = description[:max_length].rstrip() + "..."

    # Final pass: strip any lingering protocol/event tokens (defense-in-depth)
    for pattern in (r"javascript\s*:", r"data\s*:", r"vbscript\s*:", r"on\w+\s*="):
        description = re.sub(pattern, "", description, flags=re.IGNORECASE)

    return description


def validate_time_input(time_str):
    """
    Validate time input for configuration.
    
    Args:
        time_str (str): Time value as string
        
    Returns:
        tuple: (is_valid, value) where value is int if valid
    """
    try:
        value = int(time_str)
        if value < 1 or value > 1440:  # 1 minute to 24 hours
            return False, None
        return True, value
    except (ValueError, TypeError):
        return False, None
