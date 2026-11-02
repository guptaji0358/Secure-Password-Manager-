"""Persistent verification for the vault's master password."""

import base64
import hashlib
import json
import secrets
from pathlib import Path


class MasterPasswordStore:
    """Store a salted verifier without ever storing the password itself."""

    _N = 2**14
    _R = 8
    _P = 1

    def __init__(self, data_file: Path, initial_password: str):
        self.data_file = data_file
        if not self.data_file.exists():
            self._write_verifier(initial_password)

    def verify(self, password: str) -> bool:
        """Return whether *password* matches the stored verifier."""
        record = self._read_record()
        salt = base64.b64decode(record["salt"])
        expected = base64.b64decode(record["digest"])
        actual = self._derive(password, salt)
        return secrets.compare_digest(actual, expected)

    def change(self, current_password: str, new_password: str) -> bool:
        """Replace the verifier when the current password is valid."""
        if not self.verify(current_password):
            return False
        self._write_verifier(new_password)
        return True

    def _write_verifier(self, password: str) -> None:
        salt = secrets.token_bytes(16)
        record = {
            "version": 1,
            "algorithm": "scrypt",
            "salt": base64.b64encode(salt).decode("ascii"),
            "digest": base64.b64encode(self._derive(password, salt)).decode("ascii"),
        }
        self.data_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _read_record(self) -> dict:
        try:
            return json.loads(self.data_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, KeyError) as error:
            raise ValueError("The master-password settings file is invalid.") from error

    @classmethod
    def _derive(cls, password: str, salt: bytes) -> bytes:
        return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=cls._N, r=cls._R, p=cls._P)
