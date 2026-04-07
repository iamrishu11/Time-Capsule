"""
Request validation schemas for authentication endpoints.

Provides validation functions for registration and login requests.
"""

import re
from typing import Tuple, Optional, Dict, Any


def validate_email(email: str) -> bool:
    """
    Validate email format using a simple regex pattern.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    if not email:
        return False
    
    # Simple email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_registration(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate user registration request data.
    
    Args:
        data: Dictionary containing registration fields
        
    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is None
    """
    # Check for required fields
    required_fields = ['name', 'email', 'password']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"'{field}' is required"
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # Validate name
    if len(name) < 2:
        return False, "Name must be at least 2 characters long"
    
    if len(name) > 150:
        return False, "Name must not exceed 150 characters"
    
    # Validate email format
    if not validate_email(email):
        return False, "Invalid email format"
    
    if len(email) > 150:
        return False, "Email must not exceed 150 characters"
    
    # Validate password strength
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 128:
        return False, "Password must not exceed 128 characters"
    
    return True, None


def validate_login(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate user login request data.
    
    Args:
        data: Dictionary containing login fields
        
    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is None
    """
    # Check for required fields
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email:
        return False, "'email' is required"
    
    if not password:
        return False, "'password' is required"
    
    # Basic email format validation
    if not validate_email(email):
        return False, "Invalid email format"
    
    return True, None
