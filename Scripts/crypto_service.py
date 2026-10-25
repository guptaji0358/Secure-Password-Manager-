"""Encryption support for stored credentials."""

from pathlib import Path

from cryptography.fernet import Fernet


class CredentialCipher:
    """Encrypts credentials with a persistent, local Fernet key."""

    def __init__(self, key_file: Path):
        self._cipher = Fernet(self._load_or_create_key(key_file))

    @staticmethod
    def _load_or_create_key(key_file: Path) -> bytes:
        if not key_file.exists():
            key_file.write_bytes(Fernet.generate_key())
        return key_file.read_bytes()

    def encrypt(self, text: str) -> str:
        return self._cipher.encrypt(text.encode()).decode()

    def decrypt(self, text: str) -> str:
        return self._cipher.decrypt(text.encode()).decode()
