"""File-backed encrypted credential storage."""

import json
from pathlib import Path
from typing import Optional, Tuple

from .crypto_service import CredentialCipher


class CredentialStore:
    """Reads, writes, finds, and removes encrypted credentials."""

    def __init__(self, data_file: Path, cipher: CredentialCipher):
        self.data_file = data_file
        self.cipher = cipher

    def save(self, website: str, email: str, password: str) -> None:
        data = self._read_data()
        data[website] = {
            "email": self.cipher.encrypt(email),
            "password": self.cipher.encrypt(password),
        }
        self._write_data(data)

    def find(self, website: str) -> Optional[Tuple[str, str]]:
        record = self._read_data().get(website)
        if record is None:
            return None
        return self.cipher.decrypt(record["email"]), self.cipher.decrypt(record["password"])

    def delete(self, website: str) -> bool:
        data = self._read_data()
        if website not in data:
            return False
        del data[website]
        self._write_data(data)
        return True

    def _read_data(self) -> dict:
        if not self.data_file.exists():
            return {}
        try:
            with self.data_file.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_data(self, data: dict) -> None:
        with self.data_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
