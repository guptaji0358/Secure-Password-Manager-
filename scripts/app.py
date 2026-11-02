"""PySide6 user interface for the password manager."""

from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, QSize, QTimer, Qt
from PySide6.QtGui import QEnterEvent, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QFormLayout, QFrame, QGraphicsOpacityEffect, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QScrollArea, QStackedWidget, QTabWidget, QTextEdit, QToolButton, QVBoxLayout, QWidget

from .credential_store import CredentialStore
from .config import ICON_DIR, STYLESHEET_FILE
from .password_generator import generate_password


class CopyableDetailRow(QWidget):
    """A credential detail that reveals its copy control on hover."""

    def __init__(self, label: str, value: str, style_name: str):
        super().__init__()
        self.value = value
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self.detail_label = QLabel(f"{label}  {value}", objectName=style_name)
        self.detail_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.detail_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.copy_button = QToolButton(objectName="copyButton")
        self.copy_button.setIcon(QIcon(str(ICON_DIR / "copy.svg")))
        self.copy_button.setIconSize(QSize(17, 17))
        self.copy_button.setToolTip(f"Copy {label.lower()}")
        self.copy_button.setAccessibleName(f"Copy {label.lower()}")
        self.copy_button.clicked.connect(self.copy_value)
        self.copy_button.hide()
        self.opacity_effect = QGraphicsOpacityEffect(self.copy_button)
        self.opacity_effect.setOpacity(0.0)
        self.copy_button.setGraphicsEffect(self.opacity_effect)
        layout.addWidget(self.detail_label)
        layout.addStretch()
        layout.addWidget(self.copy_button)
        self._animation = None

    def enterEvent(self, event: QEnterEvent) -> None:
        self.copy_button.show()
        self._animate_opacity(self.opacity_effect.opacity(), 1.0, 150)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._animate_opacity(self.opacity_effect.opacity(), 0.0, 130, self.copy_button.hide)
        super().leaveEvent(event)

    def copy_value(self) -> None:
        clipboard = QApplication.clipboard()
        clipboard.setText(self.value)
        QTimer.singleShot(30_000, lambda: self._clear_clipboard(clipboard, self.value))
        pulse = QSequentialAnimationGroup(self)
        fade_down = QPropertyAnimation(self.opacity_effect, b"opacity", pulse)
        fade_down.setDuration(90)
        fade_down.setStartValue(1.0)
        fade_down.setEndValue(0.35)
        fade_up = QPropertyAnimation(self.opacity_effect, b"opacity", pulse)
        fade_up.setDuration(140)
        fade_up.setStartValue(0.35)
        fade_up.setEndValue(1.0)
        pulse.addAnimation(fade_down)
        pulse.addAnimation(fade_up)
        self._animation = pulse
        pulse.start()

    @staticmethod
    def _clear_clipboard(clipboard, copied_value: str) -> None:
        """Clear only the value this application placed on the clipboard."""
        if clipboard.text() == copied_value:
            clipboard.clear()

    def _animate_opacity(self, start: float, end: float, duration: int, finished=None) -> None:
        animation = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        animation.setDuration(duration)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        if finished:
            animation.finished.connect(finished)
        self._animation = animation
        animation.start()


class PasswordManagerApp(QMainWindow):
    """Modern desktop interface backed by the credential store."""

    def __init__(self, store: CredentialStore, master_password: str, image_file: str):
        super().__init__()
        self.store, self.master_password, self.image_file = store, master_password, Path(image_file)
        self.editing_website: str | None = None
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
        outer_layout.setContentsMargins(24, 30, 24, 30)
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
        tab_layout.setSpacing(14)
        form_scroll_area = QScrollArea()
        form_scroll_area.setWidgetResizable(True)
        form_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        form_content = QWidget()
        form_content_layout = QVBoxLayout(form_content)
        form_content_layout.setContentsMargins(0, 0, 8, 0)
        form_content_layout.setSpacing(0)
        card = QFrame(objectName="card")
        form = QFormLayout(card)
        form.setContentsMargins(14, 22, 14, 22)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(16)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.website_input = QLineEdit(placeholderText="example.com")
        self.email_input = QLineEdit(placeholderText="you@example.com")
        self.password_input = QLineEdit(placeholderText="Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.textChanged.connect(self.update_strength_indicator)
        password_row = QHBoxLayout()
        password_row.addWidget(self.password_input)
        generate_button = self._icon_button("spark", "Generate password")
        generate_button.clicked.connect(self.generate)
        password_row.addWidget(generate_button)
        self.show_password = QCheckBox("Show password")
        self.show_password.toggled.connect(self.toggle_password)
        self.strength_label = QLabel("Password strength: enter a password", objectName="strengthNeutral")
        self.category_input = QComboBox()
        self.category_input.addItems(["Personal", "Work", "Banking", "Social", "Other"])
        self.favorite_input = QCheckBox("Favorite")
        self.notes_input = QTextEdit(placeholderText="Recovery codes or account notes (encrypted)")
        self.notes_input.setFixedHeight(76)
        form.addRow("Website", self.website_input)
        form.addRow("Email", self.email_input)
        form.addRow("Password", password_row)
        form.addRow("Strength", self.strength_label)
        form.addRow("Category", self.category_input)
        form.addRow("", self.favorite_input)
        form.addRow("Notes", self.notes_input)
        form.addRow("", self.show_password)
        form_content_layout.addWidget(card)
        form_content_layout.addStretch()
        form_scroll_area.setWidget(form_content)
        tab_layout.addWidget(form_scroll_area, 1)
        actions = QHBoxLayout()
        delete_button = self._icon_button("delete", "Delete password", "dangerButton")
        delete_button.clicked.connect(self.delete)
        self.cancel_edit_button = QPushButton("Cancel edit")
        self.cancel_edit_button.clicked.connect(self.clear_form)
        self.cancel_edit_button.hide()
        save_button = self._icon_button("save", "Save password", "primaryButton")
        self.save_button = save_button
        save_button.clicked.connect(self.save)
        actions.addWidget(delete_button)
        actions.addWidget(self.cancel_edit_button)
        actions.addStretch()
        actions.addWidget(save_button)
        tab_layout.addLayout(actions)
        return tab

    def _create_saved_passwords_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 18, 0, 0)
        layout.setSpacing(16)
        description = QLabel("Your saved credentials are decrypted and visible in this view.", objectName="subtitle")
        description.setWordWrap(True)
        layout.addWidget(description)
        filters = QHBoxLayout()
        self.search_input = QLineEdit(placeholderText="Search website, email, or notes")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.load_saved_passwords)
        self.category_filter = QComboBox()
        self.category_filter.addItem("All categories")
        self.category_filter.addItems(["Personal", "Work", "Banking", "Social", "Other"])
        self.category_filter.currentTextChanged.connect(self.load_saved_passwords)
        self.favorites_filter = QCheckBox("Favorites only")
        self.favorites_filter.toggled.connect(self.load_saved_passwords)
        filters.addWidget(self.search_input, 1)
        filters.addWidget(self.category_filter)
        filters.addWidget(self.favorites_filter)
        layout.addLayout(filters)
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
        clipboard = QApplication.clipboard()
        clipboard.setText(password)
        QTimer.singleShot(30_000, lambda: CopyableDetailRow._clear_clipboard(clipboard, password))

    def save(self) -> None:
        website, password = self.website_input.text().strip(), self.password_input.text()
        if not website or not password:
            QMessageBox.information(self, "Missing details", "Website and password are required.")
            return
        details = (website, self.email_input.text(), password, self.notes_input.toPlainText(),
                   self.category_input.currentText().strip() or "Personal", self.favorite_input.isChecked())
        if self.editing_website:
            self.store.update(self.editing_website, *details)
        else:
            self.store.save(*details)
        self.clear_form()
        self.load_saved_passwords()
        QMessageBox.information(self, "Saved", "Credential stored securely.")

    def delete(self) -> None:
        website = self.editing_website or self.website_input.text().strip()
        if not website:
            QMessageBox.information(self, "Website needed", "Enter a website to delete.")
            return
        if not self.store.delete(website):
            QMessageBox.information(self, "Not found", "No saved record exists for this website.")
            return
        self.clear_form()
        self.load_saved_passwords()
        QMessageBox.information(self, "Deleted", "Password entry removed.")

    def toggle_password(self, visible: bool) -> None:
        self.password_input.setEchoMode(QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password)

    def update_strength_indicator(self, password: str) -> None:
        score = sum((len(password) >= 12, any(char.islower() for char in password),
                     any(char.isupper() for char in password), any(char.isdigit() for char in password),
                     any(not char.isalnum() for char in password)))
        labels = {0: ("enter a password", "strengthNeutral"), 1: ("very weak", "strengthWeak"),
                  2: ("weak", "strengthWeak"), 3: ("fair", "strengthFair"),
                  4: ("strong", "strengthStrong"), 5: ("excellent", "strengthStrong")}
        label, style = labels[score]
        self.strength_label.setText(f"Password strength: {label}")
        self.strength_label.setObjectName(style)
        self.strength_label.style().unpolish(self.strength_label)
        self.strength_label.style().polish(self.strength_label)

    def clear_form(self) -> None:
        self.editing_website = None
        self.website_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.notes_input.clear()
        self.category_input.setCurrentText("Personal")
        self.favorite_input.setChecked(False)
        self.show_password.setChecked(False)
        self.cancel_edit_button.hide()
        self.save_button.setToolTip("Save password")
        self.save_button.setAccessibleName("Save password")

    def edit_credential(self, website: str, email: str, password: str, notes: str, category: str, favorite: bool) -> None:
        self.editing_website = website
        self.website_input.setText(website)
        self.email_input.setText(email)
        self.password_input.setText(password)
        self.notes_input.setPlainText(notes)
        self.category_input.setCurrentText(category)
        self.favorite_input.setChecked(favorite)
        self.cancel_edit_button.show()
        self.save_button.setToolTip("Update password")
        self.save_button.setAccessibleName("Update password")
        self.vault_tabs.setCurrentIndex(0)
        self.website_input.setFocus()

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
        query = self.search_input.text().strip().lower()
        category = self.category_filter.currentText()
        favorites_only = self.favorites_filter.isChecked()
        matching_credentials = [
            credential for credential in credentials
            if (not query or query in " ".join(credential[:5]).lower())
            and (category == "All categories" or credential[4] == category)
            and (not favorites_only or credential[5])
        ]
        if not matching_credentials:
            empty_state = QLabel("No passwords saved yet." if not credentials else "No matching credentials found.", objectName="subtitle")
            empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.saved_passwords_layout.addWidget(empty_state)
        for website, email, password, notes, entry_category, favorite in matching_credentials:
            self.saved_passwords_layout.addWidget(
                self._credential_card(website, email, password, notes, entry_category, favorite)
            )
        self.saved_passwords_layout.addStretch()

    def _credential_card(self, website: str, email: str, password: str, notes: str,
                         category: str, favorite: bool) -> QFrame:
        card = QFrame(objectName="credentialCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        heading = QHBoxLayout()
        website_label = QLabel(("★ " if favorite else "") + website, objectName="credentialSite")
        category_label = QLabel(category, objectName="credentialCategory")
        heading.addWidget(website_label)
        heading.addStretch()
        heading.addWidget(category_label)
        layout.addLayout(heading)
        layout.addWidget(CopyableDetailRow("Email", email, "credentialDetail"))
        layout.addWidget(CopyableDetailRow("Password", password, "credentialPassword"))
        if notes:
            notes_label = QLabel(f"Notes  {notes}", objectName="credentialDetail")
            notes_label.setWordWrap(True)
            notes_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            layout.addWidget(notes_label)
        edit_button = QPushButton("Edit")
        edit_button.setToolTip(f"Edit credential for {website}")
        edit_button.clicked.connect(
            lambda: self.edit_credential(website, email, password, notes, category, favorite)
        )
        layout.addWidget(edit_button, alignment=Qt.AlignmentFlag.AlignRight)
        return card
