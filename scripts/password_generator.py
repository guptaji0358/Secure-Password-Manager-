"""Password generation helpers."""

import secrets
import string


def generate_password(length: int = 14) -> str:
    """Return a cryptographically secure random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))
