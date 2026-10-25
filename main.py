"""Application entry point."""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from scripts.app import PasswordManagerApp
from scripts.config import DATA_FILE, IMAGE_FILE, KEY_FILE, MASTER_PASSWORD
from scripts.credential_store import CredentialStore
from scripts.crypto_service import CredentialCipher


def main() -> None:
    application = QApplication(sys.argv)
    application.setWindowIcon(QIcon(str(IMAGE_FILE)))
    cipher = CredentialCipher(KEY_FILE)
    store = CredentialStore(DATA_FILE, cipher)
    window = PasswordManagerApp(store, MASTER_PASSWORD, str(IMAGE_FILE))
    window.show()
    sys.exit(application.exec())


if __name__ == "__main__":
    main()
