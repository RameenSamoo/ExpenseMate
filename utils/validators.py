import re
from datetime import datetime

def is_valid_email(email):
    """Validates email structure."""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def is_valid_password(password, min_length=6):
    """Checks password minimum length."""
    if not password or not isinstance(password, str):
        return False
    return len(password) >= min_length

def is_valid_date(date_str):
    """Validates YYYY-MM-DD date format."""
    if not date_str or not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str.strip(), '%Y-%m-%d')
        return True
    except ValueError:
        return False

def is_positive_number(val):
    """Validates positive numerical value."""
    try:
        num = float(val)
        return num > 0
    except (ValueError, TypeError):
        return False

def is_non_negative_number(val):
    """Validates non-negative numerical value."""
    try:
        num = float(val)
        return num >= 0
    except (ValueError, TypeError):
        return False

def sanitize_string(val):
    """Strips leading/trailing whitespace."""
    if val is None:
        return ""
    return str(val).strip()
