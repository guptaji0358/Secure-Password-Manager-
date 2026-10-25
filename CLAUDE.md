# Secure Password Manager — Project Memory

## Purpose

A local desktop password manager built with Python, PySide6, and Fernet encryption.
Launch it with:

```powershell
python main.py
```

## Setup

```powershell
pip install -r requirements.txt
```

Required Python version: 3.10 or newer.

## Architecture

- `main.py` creates the PySide6 application and main window.
- `scripts/app.py` contains the entire PySide6 user interface.
- `scripts/config.py` defines project-relative file locations and reads the master password from `PASSWORD_MANAGER_MASTER_PASSWORD` when present.
- `scripts/crypto_service.py` creates and uses the Fernet encryption key.
- `scripts/credential_store.py` reads, encrypts, decrypts, writes, and deletes credential records.
- `scripts/password_generator.py` generates secure random passwords.

Keep UI code in `scripts/app.py`; keep storage and encryption logic outside the UI layer.

## Sensitive Local Files

Never commit, rename, or delete these unless the user explicitly requests it:

- `secret.key` — required to decrypt all saved credentials.
- `passwords.json` — encrypted local credential data.

Both files are ignored by Git. Test storage behavior with temporary files, never with a user's real vault.

## UI Guidelines

- Use PySide6 only; do not introduce Tkinter.
- Maintain the Nightfall Vault design in `Assets/styles.qss`.
- Store action-button SVGs in `Assets/icons/`; icon-only controls must retain tooltips and accessible names.
- Preserve password masking by default and the Show Password control.
- Keep generated passwords copied to the system clipboard.

## Validation

Before completing UI changes, run at least an import/smoke test using Qt's offscreen platform:

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
python -B -c "from PySide6.QtWidgets import QApplication; from scripts.app import PasswordManagerApp; QApplication([]); print('UI import passed')"
```

Also run:

```powershell
git diff --check
```

Do not commit changes unless the user requests a commit.
