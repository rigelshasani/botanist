"""
Utility functions for Botanist.
"""

import re


def sanitize_description(description):
    """
    Sanitize user description input for security and data integrity.
    
    Args:
        description (str): Raw user input description
        
    Returns:
        str: Sanitized description
    """
    if not description or not isinstance(description, str):
        return "None provided."
    
    # Remove leading/trailing whitespace
    description = description.strip()
    
    # Return default if empty after stripping
    if not description:
        return "None provided."
    
    # Remove potentially dangerous characters and control characters
    # Keep alphanumeric, spaces, common punctuation
    description = re.sub(r'[^\w\s\-\.\,\!\?\:\;\(\)\[\]\'\"]+', '', description)
    
    # Collapse multiple spaces into single space
    description = re.sub(r'\s+', ' ', description)
    
    # Limit length to prevent extremely long descriptions
    max_length = 200
    if len(description) > max_length:
        description = description[:max_length].rstrip() + "..."
    
    # Prevent injection-style patterns
    dangerous_patterns = [
        r'<script.*?</script>',
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'on\w+\s*=',
    ]
    
    for pattern in dangerous_patterns:
        description = re.sub(pattern, '', description, flags=re.IGNORECASE)
    
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