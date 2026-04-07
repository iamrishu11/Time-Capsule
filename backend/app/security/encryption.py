"""
Encryption Helper Module

Provides symmetric encryption/decryption for capsule messages using Fernet.
Fernet is a secure, easy-to-use encryption scheme from the cryptography library
that provides authenticated encryption with AES-128-CBC.

IMPORTANT: The ENCRYPTION_KEY must be:
- A URL-safe base64-encoded 32-byte key
- Kept secret and backed up securely
- Never committed to version control

Generate a new key with:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""

import os
from cryptography.fernet import Fernet, InvalidToken

# Load encryption key from environment
_key = os.environ.get("ENCRYPTION_KEY")

# For development, generate a key if not set (NOT for production!)
if not _key:
    import warnings
    warnings.warn(
        "ENCRYPTION_KEY not set! Using auto-generated key. "
        "This is NOT safe for production - data will be lost on restart!",
        RuntimeWarning
    )
    _key = Fernet.generate_key().decode()

# Initialize Fernet cipher
try:
    fernet = Fernet(_key.encode() if isinstance(_key, str) else _key)
except Exception as e:
    raise RuntimeError(f"Invalid ENCRYPTION_KEY format: {e}")


def encrypt_text(plain_text: str) -> str:
    """
    Encrypt plaintext string using Fernet symmetric encryption.
    
    The message is encrypted with AES-128-CBC and authenticated with HMAC-SHA256.
    A timestamp is included in the token for optional TTL validation.
    
    Args:
        plain_text: The plaintext message to encrypt
        
    Returns:
        Base64-encoded encrypted token as string
        
    Example:
        >>> encrypted = encrypt_text("Hello, future!")
        >>> # Returns something like: "gAAAAABl..."
    """
    if plain_text is None:
        return None
    
    # Encode to bytes and encrypt
    token = fernet.encrypt(plain_text.encode("utf-8"))
    
    # Return as string for storage in database Text field
    return token.decode("utf-8")


def decrypt_text(cipher_text: str) -> str:
    """
    Decrypt a Fernet-encrypted token back to plaintext.
    
    Args:
        cipher_text: The encrypted token (base64 string)
        
    Returns:
        Decrypted plaintext string
        
    Raises:
        InvalidToken: If the token is invalid or tampered with
        
    Example:
        >>> decrypted = decrypt_text(encrypted_message)
        >>> # Returns: "Hello, future!"
    """
    if cipher_text is None:
        return None
    
    try:
        # Decrypt and decode to string
        plain = fernet.decrypt(cipher_text.encode("utf-8"))
        return plain.decode("utf-8")
    except InvalidToken:
        raise ValueError("Failed to decrypt: Invalid or corrupted token")
