"""Application entry point."""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from scripts.app import PasswordManagerApp
from scripts.config import DATA_FILE, IMAGE_FILE, KEY_FILE, MASTER_PASSWORD, MASTER_PASSWORD_FILE
from scripts.credential_store import CredentialStore
from scripts.crypto_service import CredentialCipher
from scripts.master_password_store import MasterPasswordStore


def main() -> None:
    application = QApplication(sys.argv)
    application.setWindowIcon(QIcon(str(IMAGE_FILE)))
    cipher = CredentialCipher(KEY_FILE)
    store = CredentialStore(DATA_FILE, cipher)
    master_password_store = MasterPasswordStore(MASTER_PASSWORD_FILE, MASTER_PASSWORD)
    window = PasswordManagerApp(store, master_password_store, str(IMAGE_FILE))
    window.show()
    sys.exit(application.exec())


if __name__ == "__main__":
    main()
