# Secure-Password-Manager-
DAY - 30/100 Project - Python X Secure Password Manager

# 🔐 Secure Password Manager (Python)

A modern desktop password manager built using **Python + PySide6** with **encryption**, **login system**, and **file-based storage**.

---

## ✨ Features

* 🔑 Master Password Login
* 🔐 Strong Encryption (Fernet / AES)
* 🎲 Password Generator
* 💾 Save / Search / Delete Passwords
* 📋 Auto Copy to Clipboard
* 👁️ Show / Hide Password
* 🖼️ Lock Image UI
* 📁 Auto File Creation
* 💾 Backup Friendly System

---

## 📂 Folder Structure

```
Secure Password Manager/
 ├── main.py
 ├── Assets/
 │   └── PASSWORD_LOCK.png
 ├── scripts/
 │   ├── app.py
 │   ├── config.py
 │   ├── credential_store.py
 │   ├── crypto_service.py
 │   └── password_generator.py
```

---

## ⚙️ Requirements

Install required packages:

```
pip install -r requirements.txt
```

Python Version:

```
Python 3.10+
```

---

## ▶️ How to Run

1. Open Terminal / CMD in the project folder.
2. Run:

```
python main.py
```

3. Enter Master Password
4. Start using the app

---

## 🔐 Security System

* All passwords are encrypted using `Fernet`
* `secret.key` is auto-generated
* Without the key, data cannot be decrypted
* Losing the key = data loss

---

## 💾 Backup (Important)

Always backup these files together:

```
passwords.json
secret.key
```

Store in USB / Drive / Cloud

---

## ⚠️ Warning

* Do NOT delete `secret.key`
* Do NOT edit encrypted data manually
* Keep backups safe

---

## 👨‍💻 Author

**Robin Gupta**

Python Developer | Learning Cyber Security

---

## 📜 License

This project is for learning and personal use.
Free to modify and improve.

---

⭐ If you like this project, give it a star on GitHub!
