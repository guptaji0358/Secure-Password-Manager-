"""Application entry point."""

import tkinter as tk

from Scripts.app import PasswordManagerApp
from Scripts.config import DATA_FILE, IMAGE_FILE, KEY_FILE, MASTER_PASSWORD
from Scripts.credential_store import CredentialStore
from Scripts.crypto_service import CredentialCipher


def main() -> None:
    root = tk.Tk()
    cipher = CredentialCipher(KEY_FILE)
    store = CredentialStore(DATA_FILE, cipher)
    PasswordManagerApp(root, store, MASTER_PASSWORD, str(IMAGE_FILE))
    root.mainloop()


if __name__ == "__main__":
    main()
