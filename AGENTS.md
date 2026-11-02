# Codex Project Memory

This file is the repository-wide instruction and memory file for Codex/GPT coding agents.

## Project

Secure Password Manager is a local PySide6 desktop application using Fernet-encrypted file storage.

```powershell
pip install -r requirements.txt
python main.py
```

Python 3.10 or newer is required.

## Code Map

- `main.py` starts the Qt application.
- `scripts/app.py` owns PySide6 windows, widgets, and user interactions.
- `scripts/config.py` defines project-relative data, asset, and icon paths.
- `scripts/credential_store.py` manages credential persistence.
- `scripts/crypto_service.py` manages Fernet encryption.
- `scripts/master_password_store.py` stores a salted master-password verifier.
- `scripts/password_generator.py` produces secure random passwords.
- `Assets/styles.qss` contains the Nightfall Vault visual theme.
- `Assets/icons/` contains the application SVG icons.

Keep UI code separate from encryption and storage logic. Use PySide6, not Tkinter.

## Sensitive Files

Never commit, rename, delete, or use real vault data in tests without explicit user approval:

- `secret.key`
- `passwords.json`
- `master_password.json`

They must remain ignored by Git. Use temporary files for storage tests.

## UI Rules

- Keep the Nightfall Vault stylesheet in `Assets/styles.qss`.
- Icon-only buttons require meaningful tooltips and accessible names.
- Passwords are hidden in input fields by default.
- Saved credential cards include clipboard-copy support for email and password.
- The Settings tab changes the persistent master password; it stores only a salted verifier and locks the vault after a successful change.
- The login screen automatically unlocks shortly after the correct master password is entered.

## Validation

Run an offscreen UI smoke test and whitespace check before completing UI changes:

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
python -B -c "from PySide6.QtWidgets import QApplication; from scripts.app import PasswordManagerApp; QApplication([]); print('UI import passed')"
git diff --check
```

Do not commit or push unless the user asks.

## Future Feature TODOs

- Add encrypted export/import backups, including recovery guidance and safe overwrite handling.
- Add local TOTP authenticator-code generation from encrypted secrets.
- Add an inactivity auto-lock timer that returns the vault to the master-password screen.
