"""Application paths and configuration."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "passwords.json"
KEY_FILE = BASE_DIR / "secret.key"
MASTER_PASSWORD_FILE = BASE_DIR / "master_password.json"
IMAGE_FILE = BASE_DIR / "Assets" / "PASSWORD_LOCK.png"
STYLESHEET_FILE = BASE_DIR / "Assets" / "styles.qss"
ICON_DIR = BASE_DIR / "Assets" / "icons"

# Used only to migrate installations created before persistent master-password
# settings were introduced. After the first launch, authentication uses the
# verifier in MASTER_PASSWORD_FILE instead.
MASTER_PASSWORD = os.getenv("PASSWORD_MANAGER_MASTER_PASSWORD", "1234")
