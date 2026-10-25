"""Application paths and configuration."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "passwords.json"
KEY_FILE = BASE_DIR / "secret.key"
IMAGE_FILE = BASE_DIR / "Assets" / "PASSWORD_LOCK.png"
STYLESHEET_FILE = BASE_DIR / "Assets" / "styles.qss"
ICON_DIR = BASE_DIR / "Assets" / "icons"

# Set PASSWORD_MANAGER_MASTER_PASSWORD in your environment before using this
# application outside a learning/demo setting.
MASTER_PASSWORD = os.getenv("PASSWORD_MANAGER_MASTER_PASSWORD", "1234")
