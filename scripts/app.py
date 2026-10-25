"""PySide6 user interface for the password manager."""

from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QCheckBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QScrollArea, QStackedWidget, QTabWidget, QVBoxLayout, QWidget

from .credential_store import CredentialStore
from .config import ICON_DIR, STYLESHEET_FILE
from .password_generator import generate_password


class PasswordManagerApp(QMainWindow):
    """Modern desktop interface backed by the credential store."""

    def __init__(self, store: CredentialStore, master_password: str, image_file: str):
        super().__init__()
        self.store, self.master_password, self.image_file = store, master_password, Path(image_file)
        self.setWindowTitle("Secure Password Manager")
        self.setWindowIcon(QIcon(str(self.image_file)))
        self.setMinimumSize(620, 560)
        self.setStyleSheet(STYLESHEET_FILE.read_text(encoding="utf-8"))
        self.pages = QStackedWidget()
        self.pages.addWidget(self._create_login_page())
        self.pages.addWidget(self._create_manager_page())
        self.setCentralWidget(self.pages)

    def _create_login_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(72, 48, 72, 48)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(str(self.image_file))
        if pixmap.isNull():
            image.setText("🔐")
            image.setStyleSheet("font-size: 72px;")
        else:
            image.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(image)
        layout.addWidget(QLabel("Welcome back", objectName="title", alignment=Qt.AlignmentFlag.AlignCenter))
        layout.addWidget(QLabel("Enter your master password to unlock your vault.", objectName="subtitle", alignment=Qt.AlignmentFlag.AlignCenter))
        self.login_input = QLineEdit(placeholderText="Master password")
        self.login_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_input.returnPressed.connect(self.login)
        layout.addWidget(self.login_input)
        login_button = self._icon_button("unlock", "Unlock vault", "primaryButton")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)
        return page

    def _create_manager_page(self) -> QWidget:
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(48, 36, 48, 36)
        outer_layout.setSpacing(22)
        outer_layout.addWidget(QLabel("Password vault", objectName="title"))
        outer_layout.addWidget(QLabel("Save and retrieve encrypted credentials.", objectName="subtitle"))
        self.vault_tabs = QTabWidget()
        self.vault_tabs.addTab(self._create_add_password_tab(), "Add password")
        self.vault_tabs.addTab(self._create_saved_passwords_tab(), "Saved passwords")
        self.vault_tabs.currentChanged.connect(self._handle_tab_change)
        outer_layout.addWidget(self.vault_tabs)
        return page

    def _create_add_password_tab(self) -> QWidget:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 18, 0, 0)
        tab_layout.setSpacing(22)
        card = QFrame(objectName="card")
        form = QFormLayout(card)
        form.setContentsMargins(28, 28, 28, 28)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(16)
        self.website_input = QLineEdit(placeholderText="example.com")
        self.email_input = QLineEdit(placeholderText="you@example.com")
        self.password_input = QLineEdit(placeholderText="Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_row = QHBoxLayout()
        password_row.addWidget(self.password_input)
        generate_button = self._icon_button("spark", "Generate password")
        generate_button.clicked.connect(self.generate)
        password_row.addWidget(generate_button)
        self.show_password = QCheckBox("Show password")
        self.show_password.toggled.connect(self.toggle_password)
        form.addRow("Website", self.website_input)
        form.addRow("Email", self.email_input)
        form.addRow("Password", password_row)
        form.addRow("", self.show_password)
        tab_layout.addWidget(card)
        actions = QHBoxLayout()
        delete_button = self._icon_button("delete", "Delete password", "dangerButton")
        delete_button.clicked.connect(self.delete)
        save_button = self._icon_button("save", "Save password", "primaryButton")
        save_button.clicked.connect(self.save)
        actions.addWidget(delete_button)
        actions.addStretch()
        actions.addWidget(save_button)
        tab_layout.addLayout(actions)
        tab_layout.addStretch()
        return tab

    def _create_saved_passwords_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 18, 0, 0)
        layout.setSpacing(16)
        description = QLabel("Your saved credentials are decrypted and visible in this view.", objectName="subtitle")
        layout.addWidget(description)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.saved_passwords_content = QWidget()
        self.saved_passwords_layout = QVBoxLayout(self.saved_passwords_content)
        self.saved_passwords_layout.setContentsMargins(0, 0, 8, 0)
        self.saved_passwords_layout.setSpacing(12)
        scroll_area.setWidget(self.saved_passwords_content)
        layout.addWidget(scroll_area)
        refresh_button = self._icon_button("refresh", "Refresh saved passwords")
        refresh_button.clicked.connect(self.load_saved_passwords)
        layout.addWidget(refresh_button, alignment=Qt.AlignmentFlag.AlignRight)
        return tab

    def login(self) -> None:
        if self.login_input.text() != self.master_password:
            QMessageBox.warning(self, "Incorrect password", "The master password is incorrect.")
            self.login_input.selectAll()
            self.login_input.setFocus()
            return
        self.login_input.clear()
        self.pages.setCurrentIndex(1)
        self.website_input.setFocus()

    def generate(self) -> None:
        password = generate_password()
        self.password_input.setText(password)
        QApplication.clipboard().setText(password)

    def save(self) -> None:
        website, password = self.website_input.text().strip(), self.password_input.text()
        if not website or not password:
            QMessageBox.information(self, "Missing details", "Website and password are required.")
            return
        self.store.save(website, self.email_input.text(), password)
        self.website_input.clear()
        self.password_input.clear()
        self.load_saved_passwords()
        QMessageBox.information(self, "Saved", "Password stored securely.")

    def delete(self) -> None:
        website = self.website_input.text().strip()
        if not website:
            QMessageBox.information(self, "Website needed", "Enter a website to delete.")
            return
        if not self.store.delete(website):
            QMessageBox.information(self, "Not found", "No saved record exists for this website.")
            return
        self.website_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.load_saved_passwords()
        QMessageBox.information(self, "Deleted", "Password entry removed.")

    def toggle_password(self, visible: bool) -> None:
        self.password_input.setEchoMode(QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password)

    @staticmethod
    def _icon_button(icon_name: str, label: str, object_name: str | None = None) -> QPushButton:
        button = QPushButton()
        if object_name:
            button.setObjectName(object_name)
        button.setIcon(QIcon(str(ICON_DIR / f"{icon_name}.svg")))
        button.setIconSize(QSize(20, 20))
        button.setToolTip(label)
        button.setAccessibleName(label)
        button.setProperty("iconOnly", True)
        return button

    def _handle_tab_change(self, index: int) -> None:
        if index == 1:
            self.load_saved_passwords()

    def load_saved_passwords(self) -> None:
        try:
            credentials = self.store.all_credentials()
        except Exception:
            QMessageBox.critical(self, "Unable to decrypt", "One or more records could not be decrypted with the current key.")
            return
        while self.saved_passwords_layout.count():
            item = self.saved_passwords_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not credentials:
            empty_state = QLabel("No passwords saved yet.", objectName="subtitle")
            empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.saved_passwords_layout.addWidget(empty_state)
        for website, email, password in credentials:
            self.saved_passwords_layout.addWidget(self._credential_card(website, email, password))
        self.saved_passwords_layout.addStretch()

    @staticmethod
    def _credential_card(website: str, email: str, password: str) -> QFrame:
        card = QFrame(objectName="credentialCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        website_label = QLabel(website, objectName="credentialSite")
        email_label = QLabel(f"Email  {email}", objectName="credentialDetail")
        password_label = QLabel(f"Password  {password}", objectName="credentialPassword")
        password_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(website_label)
        layout.addWidget(email_label)
        layout.addWidget(password_label)
        return card
