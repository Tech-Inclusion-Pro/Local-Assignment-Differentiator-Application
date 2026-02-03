#!/usr/bin/env python3
"""
Assignment Differentiation Application - Python Desktop Application
A tool for creating differentiated learning materials using Universal Design for Learning principles
and local AI (Ollama) for content generation.
"""

import sys
import os
from datetime import datetime
from typing import Optional
from functools import partial

# Handle PyInstaller bundled app paths
if getattr(sys, 'frozen', False):
    # Running as bundled app
    bundle_dir = sys._MEIPASS
    sys.path.insert(0, bundle_dir)
else:
    # Running as script
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
    QComboBox, QGroupBox, QScrollArea, QFrame, QProgressBar,
    QMessageBox, QFileDialog, QDialog, QDialogButtonBox, QCheckBox,
    QTabWidget, QSplitter, QSizePolicy, QListView, QInputDialog,
    QListWidget, QListWidgetItem, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap

from ollama_service import OllamaService, build_system_prompt, build_conversation_prompt
from export_service import (
    export_to_docx, export_to_pdf, export_to_pptx, export_all_to_xlsx,
    VERSION_NAMES
)
from storage_service import StorageService, get_default_form_data
from auth_service import AuthService, get_security_questions_list

# ============================================================================
# Brand Colors and Accessibility Constants (WCAG 2.1 AA Compliant)
# ============================================================================

# Primary colors - Purple Palette (matching accessible-pdf-toolkit)
COLOR_PRIMARY = "#a23b84"          # Primary Purple
COLOR_PRIMARY_DARK = "#8a3270"     # Darker Primary
COLOR_PRIMARY_LIGHT = "#b85a9a"    # Lighter Primary

# Secondary colors
COLOR_SECONDARY = "#3a2b95"        # Secondary Purple
COLOR_SECONDARY_DARK = "#2e2277"   # Darker Secondary
COLOR_SECONDARY_LIGHT = "#4d3cad"  # Lighter Secondary

# Accent colors
COLOR_ACCENT = "#6f2fa6"           # Accent Purple

# Semantic colors
COLOR_SUCCESS = "#22C55E"          # Green
COLOR_WARNING = "#F59E0B"          # Amber
COLOR_ERROR = "#EF4444"            # Red
COLOR_INFO = "#3B82F6"             # Blue

# Dark theme colors (default)
COLOR_BACKGROUND = "#1a1a2e"       # Dark blue-gray
COLOR_BACKGROUND_ALT = "#16213e"   # Slightly lighter
COLOR_SURFACE = "#1f2847"          # Card/panel background
COLOR_BORDER = "#4a5568"           # Gray 600
COLOR_TEXT_PRIMARY = "#FFFFFF"     # White text
COLOR_TEXT_SECONDARY = "#CBD5E1"   # Light gray text

# Input field colors
COLOR_INPUT_BG = "#2d3748"         # Dark input background
COLOR_INPUT_TEXT = "#FFFFFF"       # White input text
COLOR_INPUT_BORDER = "#4a5568"     # Gray border
COLOR_INPUT_FOCUS = "#3B82F6"      # Blue focus ring

# Legacy color names for compatibility
COLOR_TEXT_LIGHT = "#FFFFFF"
COLOR_TEXT_DARK = "#1a1a1a"
COLOR_BG_LIGHT = "#f5f0f8"
COLOR_BG_WHITE = "#FFFFFF"
COLOR_FOCUS = "#3B82F6"

# Minimum touch target size (44x44 px per WCAG)
MIN_TOUCH_TARGET = 44

# Application name
APP_NAME = "Assignment Differentiation Application"
APP_SUBTITLE = "Universal Design for Learning Materials"


# ============================================================================
# Worker Threads for AI Operations
# ============================================================================

class GenerationWorker(QThread):
    """Background thread for generating materials."""
    progress = pyqtSignal(str, int)  # version_key, percentage
    version_complete = pyqtSignal(str, dict)  # version_key, result
    finished = pyqtSignal(dict)  # all results
    error = pyqtSignal(str)

    def __init__(self, ollama: OllamaService, form_data: dict):
        super().__init__()
        self.ollama = ollama
        self.form_data = form_data

    def run(self):
        results = {}
        versions = ['simplified', 'on_level', 'enriched', 'visual_heavy', 'scaffolded']

        for i, version in enumerate(versions):
            try:
                self.progress.emit(version, 0)

                system_prompt = build_system_prompt(self.form_data, version)
                user_prompt = f"""Please create {VERSION_NAMES[version]} learning materials for the following:

Learning Objective: {self.form_data.get('learning_objective')}
Grade Level: {self.form_data.get('grade_level')}
Subject: {self.form_data.get('subject', 'Not specified')}
Student Needs: {self.form_data.get('student_needs')}

Create comprehensive, engaging materials following the format specified."""

                content = self.ollama.generate(user_prompt, system_prompt)

                results[version] = {
                    'name': VERSION_NAMES[version],
                    'content': content,
                    'generated_at': datetime.now().isoformat(),
                    'error': None
                }

                self.version_complete.emit(version, results[version])
                self.progress.emit(version, 100)

            except Exception as e:
                results[version] = {
                    'name': VERSION_NAMES[version],
                    'content': '',
                    'generated_at': datetime.now().isoformat(),
                    'error': str(e)
                }
                self.version_complete.emit(version, results[version])

        self.finished.emit(results)


class ChatWorker(QThread):
    """Background thread for AI chat."""
    response_chunk = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, ollama: OllamaService, messages: list, system_prompt: str):
        super().__init__()
        self.ollama = ollama
        self.messages = messages
        self.system_prompt = system_prompt

    def run(self):
        try:
            response = self.ollama.chat(
                self.messages,
                self.system_prompt,
                on_progress=lambda chunk: self.response_chunk.emit(chunk)
            )
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


# ============================================================================
# Authentication Widgets (Dark Theme - matching accessible-pdf-toolkit)
# ============================================================================

class AuthDialog(QWidget):
    """Combined Login/Registration dialog with tabbed interface (dark theme)."""

    authenticated = pyqtSignal(str)  # Emits username on successful login

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth = auth_service
        self.security_questions = get_security_questions_list()
        self.setup_ui()
        self.setup_accessibility()

    def setup_ui(self):
        """Set up the dialog UI with dark theme."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLOR_BACKGROUND};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # Center content
        layout.addStretch(1)

        # Logo image
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(bundle_dir, 'assets', 'ADA App.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(
                150, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_pixmap)
        logo_label.setAccessibleName("Application logo")
        layout.addWidget(logo_label)

        # App Title
        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {COLOR_PRIMARY};
            margin-bottom: 16px;
        """)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel(APP_SUBTITLE)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12pt;")
        layout.addWidget(subtitle)

        layout.addSpacing(16)

        # Tab widget for login/register - centered with max width
        tab_container = QWidget()
        tab_container.setMaximumWidth(480)
        tab_layout = QVBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                background-color: {COLOR_BACKGROUND};
                padding: 16px;
            }}
            QTabBar::tab {{
                padding: 8px 24px;
                margin-right: 4px;
                background-color: {COLOR_BACKGROUND_ALT};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                border-bottom: none;
                border-radius: 4px 4px 0 0;
                font-size: 12pt;
            }}
            QTabBar::tab:selected {{
                background-color: {COLOR_PRIMARY};
                color: white;
            }}
        """)

        # Login tab
        login_tab = QWidget()
        login_layout = QVBoxLayout(login_tab)
        login_layout.setSpacing(2)
        login_layout.setContentsMargins(16, 16, 16, 16)

        # Username field
        login_layout.addWidget(self._create_field_label("Username"))
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username")
        self.login_username.setAccessibleName("Login username")
        self._style_input(self.login_username)
        login_layout.addWidget(self.login_username)
        login_layout.addSpacing(18)

        # Password field
        login_layout.addWidget(self._create_field_label("Password"))
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password.setAccessibleName("Login password")
        self.login_password.returnPressed.connect(self._login)
        self._style_input(self.login_password)
        login_layout.addWidget(self.login_password)
        login_layout.addSpacing(12)

        # Stay logged in checkbox
        self.stay_logged_in_cb = QCheckBox("Stay logged in")
        self.stay_logged_in_cb.setAccessibleName("Stay logged in checkbox")
        self.stay_logged_in_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {COLOR_TEXT_PRIMARY};
                font-size: 12pt;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLOR_PRIMARY};
                border: 2px solid {COLOR_PRIMARY};
                border-radius: 3px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {COLOR_INPUT_BG};
                border: 2px solid {COLOR_BORDER};
                border-radius: 3px;
            }}
        """)
        login_layout.addWidget(self.stay_logged_in_cb)
        login_layout.addSpacing(12)

        # Login error label
        self.login_error_label = QLabel("")
        self.login_error_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: bold;")
        self.login_error_label.setWordWrap(True)
        self.login_error_label.hide()
        login_layout.addWidget(self.login_error_label)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self._login)
        login_btn.setStyleSheet(self._get_primary_button_style())
        login_btn.setFixedHeight(44)
        login_layout.addWidget(login_btn)
        login_layout.addSpacing(12)

        # Forgot password link
        forgot_password_btn = QPushButton("Forgot Password?")
        forgot_password_btn.clicked.connect(self._show_password_recovery)
        forgot_password_btn.setStyleSheet(f"""
            QPushButton {{
                background: none;
                border: none;
                color: {COLOR_PRIMARY_LIGHT};
                text-decoration: underline;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                color: {COLOR_PRIMARY};
            }}
        """)
        forgot_password_btn.setAccessibleName("Forgot password link")
        login_layout.addWidget(forgot_password_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        login_layout.addStretch()
        self.tabs.addTab(login_tab, "Login")

        # Register tab with scroll area for security questions
        register_tab = QWidget()
        register_scroll = QScrollArea()
        register_scroll.setWidgetResizable(True)
        register_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {COLOR_BACKGROUND};
            }}
            QScrollBar:vertical {{
                background-color: {COLOR_BACKGROUND_ALT};
                width: 12px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLOR_BORDER};
                border-radius: 6px;
                min-height: 20px;
            }}
        """)

        register_content = QWidget()
        register_layout = QVBoxLayout(register_content)
        register_layout.setSpacing(2)
        register_layout.setContentsMargins(16, 8, 16, 8)

        # Username field
        register_layout.addWidget(self._create_field_label("Username"))
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("At least 3 characters")
        self.reg_username.setAccessibleName("Registration username")
        self._style_input(self.reg_username)
        register_layout.addWidget(self.reg_username)
        register_layout.addSpacing(12)

        # Password field
        register_layout.addWidget(self._create_field_label("Password"))
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("At least 6 characters")
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password.setAccessibleName("Registration password")
        self._style_input(self.reg_password)
        register_layout.addWidget(self.reg_password)
        register_layout.addSpacing(12)

        # Confirm Password field
        register_layout.addWidget(self._create_field_label("Confirm Password"))
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Re-enter your password")
        self.reg_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_confirm.setAccessibleName("Confirm password")
        self._style_input(self.reg_confirm)
        register_layout.addWidget(self.reg_confirm)
        register_layout.addSpacing(16)

        # Security Questions Section
        security_header = QLabel("Security Questions (for password recovery)")
        security_header.setStyleSheet(f"""
            font-weight: bold;
            font-size: 13pt;
            color: {COLOR_PRIMARY_LIGHT};
            padding-top: 8px;
            padding-bottom: 4px;
        """)
        register_layout.addWidget(security_header)

        security_note = QLabel("Answers are NOT case sensitive")
        security_note.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 10pt; font-style: italic;")
        register_layout.addWidget(security_note)
        register_layout.addSpacing(8)

        # Security questions and answers
        self.question_combos = []
        self.answer_inputs = []

        for i in range(3):
            register_layout.addWidget(self._create_field_label(f"Security Question {i+1}"))
            combo = self._create_security_question_combo(f"Security question {i+1}")
            register_layout.addWidget(combo)
            self.question_combos.append(combo)

            answer = QLineEdit()
            answer.setPlaceholderText("Your answer")
            answer.setAccessibleName(f"Answer to security question {i+1}")
            self._style_input(answer)
            register_layout.addWidget(answer)
            self.answer_inputs.append(answer)
            register_layout.addSpacing(10)

        # Register error label
        self.reg_error_label = QLabel("")
        self.reg_error_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: bold;")
        self.reg_error_label.setWordWrap(True)
        self.reg_error_label.hide()
        register_layout.addWidget(self.reg_error_label)

        # Create Account button
        register_btn = QPushButton("Create Account")
        register_btn.clicked.connect(self._register)
        register_btn.setStyleSheet(self._get_primary_button_style())
        register_btn.setFixedHeight(44)
        register_layout.addWidget(register_btn)

        register_layout.addStretch()

        register_scroll.setWidget(register_content)
        register_tab_layout = QVBoxLayout(register_tab)
        register_tab_layout.setContentsMargins(0, 0, 0, 0)
        register_tab_layout.addWidget(register_scroll)
        self.tabs.addTab(register_tab, "Register")

        tab_layout.addWidget(self.tabs)

        # Center the tab container
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(tab_container)
        h_layout.addStretch()
        layout.addLayout(h_layout)

        layout.addStretch(1)

    def _create_field_label(self, text: str) -> QLabel:
        """Create a styled field label."""
        label = QLabel(text)
        label.setStyleSheet(f"""
            font-weight: bold;
            font-size: 12pt;
            color: {COLOR_TEXT_PRIMARY};
        """)
        return label

    def _create_security_question_combo(self, accessible_name: str) -> QComboBox:
        """Create a styled security question combo box."""
        combo = QComboBox()
        combo.setView(QListView())
        combo.addItems(["Select a question..."] + self.security_questions)
        combo.setAccessibleName(accessible_name)
        combo.setFixedHeight(40)
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_TEXT};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12pt;
            }}
            QComboBox:focus {{
                border: 2px solid {COLOR_INPUT_FOCUS};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLOR_TEXT_PRIMARY};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_TEXT};
                selection-background-color: {COLOR_PRIMARY};
                selection-color: white;
                border: 1px solid {COLOR_INPUT_BORDER};
            }}
        """)
        return combo

    def _style_input(self, widget):
        """Apply dark theme styling to input fields."""
        widget.setMinimumHeight(44)
        widget.setFont(QFont("Arial", 14))
        widget.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_TEXT};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 6px;
                padding: 12px 14px;
                font-size: 14pt;
                min-height: 24px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_INPUT_FOCUS};
            }}
            QLineEdit::placeholder {{
                color: {COLOR_TEXT_SECONDARY};
            }}
        """)

    def _get_primary_button_style(self) -> str:
        """Get primary button stylesheet."""
        return f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_DARK};
            }}
            QPushButton:focus {{
                outline: 2px solid {COLOR_PRIMARY_LIGHT};
                outline-offset: 2px;
            }}
        """

    def setup_accessibility(self):
        """Set up accessibility features."""
        self.setAccessibleName("Login dialog")
        self.setAccessibleDescription("Login or create an account to continue")

    def _login(self):
        """Handle login attempt."""
        username = self.login_username.text().strip()
        password = self.login_password.text()
        stay_logged_in = self.stay_logged_in_cb.isChecked()

        if not username or not password:
            self._show_login_error("Please enter username and password")
            return

        success, message = self.auth.login(username, password, stay_logged_in=stay_logged_in)
        if success:
            self.login_error_label.hide()
            self.authenticated.emit(username)
        else:
            self._show_login_error(message)
            self.login_password.clear()
            self.login_password.setFocus()

    def _register(self):
        """Handle registration attempt."""
        username = self.reg_username.text().strip()
        password = self.reg_password.text()
        confirm = self.reg_confirm.text()

        # Validation
        if not username:
            self._show_reg_error("Username is required")
            return
        if len(username) < 3:
            self._show_reg_error("Username must be at least 3 characters")
            return
        if not password:
            self._show_reg_error("Password is required")
            return
        if len(password) < 6:
            self._show_reg_error("Password must be at least 6 characters")
            return
        if password != confirm:
            self._show_reg_error("Passwords do not match")
            return

        # Validate security questions
        security_questions = []
        selected_questions = set()

        for i in range(3):
            q_index = self.question_combos[i].currentIndex()
            if q_index == 0:
                self._show_reg_error(f"Please select security question {i+1}")
                return

            question = self.question_combos[i].currentText()
            if question in selected_questions:
                self._show_reg_error("Please select different questions for each security question")
                return
            selected_questions.add(question)

            answer = self.answer_inputs[i].text().strip()
            if not answer:
                self._show_reg_error(f"Please provide an answer for security question {i+1}")
                return

            security_questions.append({'question': question, 'answer': answer})

        # Attempt registration
        success, message = self.auth.register(username, password, security_questions)
        if success:
            self.reg_error_label.hide()
            QMessageBox.information(
                self, "Success",
                "Account created successfully!\n\n"
                "Your security questions have been saved for password recovery."
            )
            # Switch to login tab and auto-fill username
            self.login_username.setText(username)
            self.login_password.clear()
            self.tabs.setCurrentIndex(0)
            self.login_password.setFocus()
        else:
            self._show_reg_error(message)

    def _show_login_error(self, message: str):
        """Display login error message."""
        self.login_error_label.setText(message)
        self.login_error_label.show()

    def _show_reg_error(self, message: str):
        """Display registration error message."""
        self.reg_error_label.setText(message)
        self.reg_error_label.show()

    def _show_password_recovery(self):
        """Show the password recovery dialog."""
        dialog = PasswordRecoveryDialog(self.auth, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.login_password.clear()
            QMessageBox.information(
                self, "Password Reset",
                "Your password has been reset successfully.\n"
                "Please log in with your new password."
            )

    def clear_form(self):
        """Clear all form fields."""
        self.login_username.clear()
        self.login_password.clear()
        self.login_error_label.hide()
        self.reg_username.clear()
        self.reg_password.clear()
        self.reg_confirm.clear()
        for combo in self.question_combos:
            combo.setCurrentIndex(0)
        for answer in self.answer_inputs:
            answer.clear()
        self.reg_error_label.hide()


class PasswordRecoveryDialog(QDialog):
    """Dialog for recovering password using security questions (dark theme)."""

    def __init__(self, auth_service: AuthService, parent=None):
        super().__init__(parent)
        self.auth = auth_service
        self.current_username = ""
        self.questions = []
        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Password Recovery")
        self.setFixedSize(450, 550)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR_BACKGROUND};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # Title
        title = QLabel("Password Recovery")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLOR_PRIMARY};
            margin-bottom: 8px;
        """)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Enter your username and answer your security questions.\n"
            "Answers are NOT case sensitive."
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11pt;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        layout.addSpacing(8)

        # Username field
        layout.addWidget(self._create_label("Username"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setAccessibleName("Recovery username")
        self._apply_input_style(self.username_input)
        layout.addWidget(self.username_input)

        # Lookup button
        lookup_btn = QPushButton("Look Up Security Questions")
        lookup_btn.clicked.connect(self._lookup_questions)
        lookup_btn.setStyleSheet(self._get_secondary_button_style())
        lookup_btn.setFixedHeight(40)
        layout.addWidget(lookup_btn)
        layout.addSpacing(8)

        # Security questions container (hidden initially)
        self.questions_container = QWidget()
        self.questions_container.setVisible(False)
        questions_layout = QVBoxLayout(self.questions_container)
        questions_layout.setContentsMargins(0, 0, 0, 0)
        questions_layout.setSpacing(8)

        # Question labels and answer fields
        self.question_labels = []
        self.answer_inputs = []

        for i in range(3):
            q_label = QLabel("")
            q_label.setWordWrap(True)
            q_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 11pt; font-weight: bold;")
            questions_layout.addWidget(q_label)
            self.question_labels.append(q_label)

            a_input = QLineEdit()
            a_input.setPlaceholderText("Your answer")
            self._apply_input_style(a_input)
            questions_layout.addWidget(a_input)
            self.answer_inputs.append(a_input)
            questions_layout.addSpacing(8)

        layout.addWidget(self.questions_container)

        # New password container (hidden initially)
        self.password_container = QWidget()
        self.password_container.setVisible(False)
        password_layout = QVBoxLayout(self.password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(8)

        password_layout.addWidget(self._create_label("New Password"))
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Enter new password (min 6 characters)")
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._apply_input_style(self.new_password)
        password_layout.addWidget(self.new_password)

        password_layout.addWidget(self._create_label("Confirm New Password"))
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm new password")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._apply_input_style(self.confirm_password)
        password_layout.addWidget(self.confirm_password)

        layout.addWidget(self.password_container)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLOR_ERROR}; font-weight: bold;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(self._get_secondary_button_style())
        cancel_btn.setFixedHeight(44)
        button_layout.addWidget(cancel_btn)

        self.verify_btn = QPushButton("Verify Answers")
        self.verify_btn.clicked.connect(self._verify_answers)
        self.verify_btn.setStyleSheet(self._get_primary_button_style())
        self.verify_btn.setFixedHeight(44)
        self.verify_btn.setVisible(False)
        button_layout.addWidget(self.verify_btn)

        self.reset_btn = QPushButton("Reset Password")
        self.reset_btn.clicked.connect(self._reset_password)
        self.reset_btn.setStyleSheet(self._get_primary_button_style())
        self.reset_btn.setFixedHeight(44)
        self.reset_btn.setVisible(False)
        button_layout.addWidget(self.reset_btn)

        layout.addLayout(button_layout)

    def _create_label(self, text: str) -> QLabel:
        """Create a styled label."""
        label = QLabel(text)
        label.setStyleSheet(f"font-weight: bold; font-size: 11pt; color: {COLOR_TEXT_PRIMARY};")
        return label

    def _apply_input_style(self, widget: QLineEdit):
        """Apply input field styling."""
        widget.setFixedHeight(40)
        widget.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_TEXT};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12pt;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_INPUT_FOCUS};
            }}
        """)

    def _get_primary_button_style(self) -> str:
        """Get primary button stylesheet."""
        return f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_DARK};
            }}
        """

    def _get_secondary_button_style(self) -> str:
        """Get secondary button stylesheet."""
        return f"""
            QPushButton {{
                background-color: {COLOR_BACKGROUND_ALT};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                padding: 12px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_SURFACE};
            }}
        """

    def _lookup_questions(self):
        """Look up security questions for the username."""
        username = self.username_input.text().strip()
        if not username:
            self._show_error("Please enter your username")
            return

        questions = self.auth.get_security_questions(username)
        if not questions:
            self._show_error("Username not found or no security questions set up.")
            return

        self.current_username = username
        self.questions = questions

        for i, q in enumerate(questions):
            self.question_labels[i].setText(f"{i+1}. {q}")

        # Show questions and verify button
        self.questions_container.setVisible(True)
        self.verify_btn.setVisible(True)
        self.username_input.setEnabled(False)
        self.error_label.hide()

    def _verify_answers(self):
        """Verify the security question answers."""
        answers = [inp.text().strip() for inp in self.answer_inputs]

        for i, ans in enumerate(answers):
            if not ans:
                self._show_error(f"Please answer question {i+1}")
                return

        success, message = self.auth.verify_security_answers(self.current_username, answers)
        if success:
            # Show password reset fields
            self.password_container.setVisible(True)
            self.reset_btn.setVisible(True)
            self.verify_btn.setVisible(False)

            # Disable answer fields
            for inp in self.answer_inputs:
                inp.setEnabled(False)

            self.error_label.hide()
        else:
            self._show_error("One or more answers are incorrect. Please try again.")

    def _reset_password(self):
        """Reset the password after verification."""
        new_pass = self.new_password.text()
        confirm_pass = self.confirm_password.text()

        if not new_pass:
            self._show_error("Please enter a new password")
            return

        if len(new_pass) < 6:
            self._show_error("Password must be at least 6 characters")
            return

        if new_pass != confirm_pass:
            self._show_error("Passwords do not match")
            return

        answers = [inp.text().strip() for inp in self.answer_inputs]
        success, message = self.auth.reset_password(self.current_username, new_pass, answers)
        if success:
            self.accept()
        else:
            self._show_error(f"Failed to reset password: {message}")

    def _show_error(self, message: str):
        """Display error message."""
        self.error_label.setText(message)
        self.error_label.show()


# Legacy classes for compatibility (redirect to AuthDialog)
class LoginWidget(QWidget):
    """Legacy LoginWidget - now redirects to AuthDialog."""
    login_successful = pyqtSignal(str)
    register_requested = pyqtSignal()
    forgot_password_requested = pyqtSignal()

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth = auth_service

    def clear_form(self):
        pass


class RegisterWidget(QWidget):
    """Legacy RegisterWidget - now handled by AuthDialog."""
    registration_successful = pyqtSignal(str)
    back_to_login = pyqtSignal()

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth = auth_service

    def clear_form(self):
        pass


class ForgotPasswordWidget(QWidget):
    """Legacy ForgotPasswordWidget - now handled by PasswordRecoveryDialog."""
    password_reset_successful = pyqtSignal()
    back_to_login = pyqtSignal()

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth = auth_service

    def reset_form(self):
        pass


class AuthStackedWidget(QStackedWidget):
    """Authentication widget - now uses unified AuthDialog with dark theme."""

    authenticated = pyqtSignal(str)  # Emits username when authenticated

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth = auth_service

        # Use the new unified AuthDialog
        self.auth_dialog = AuthDialog(auth_service)
        self.auth_dialog.authenticated.connect(self.on_login_success)

        # Add to stack
        self.addWidget(self.auth_dialog)

    def on_login_success(self, username: str):
        self.authenticated.emit(username)

    def show_login(self):
        self.auth_dialog.clear_form()
        self.auth_dialog.tabs.setCurrentIndex(0)
        self.setCurrentWidget(self.auth_dialog)


# ============================================================================
# Settings Dialog
# ============================================================================

class SettingsDialog(QDialog):
    """Dialog for configuring Ollama and app settings (dark theme)."""

    def __init__(self, storage: StorageService, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        # Apply dark theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR_BACKGROUND};
            }}
            QLabel {{
                color: {COLOR_TEXT_PRIMARY};
            }}
            QGroupBox {{
                font-weight: bold;
                color: {COLOR_PRIMARY_LIGHT};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QLineEdit {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_TEXT};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 4px;
                padding: 8px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_INPUT_FOCUS};
            }}
            QComboBox {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_TEXT};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 4px;
                padding: 8px;
            }}
            QComboBox:focus {{
                border: 2px solid {COLOR_INPUT_FOCUS};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLOR_TEXT_PRIMARY};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_TEXT};
                selection-background-color: {COLOR_PRIMARY};
                selection-color: white;
                border: 1px solid {COLOR_INPUT_BORDER};
            }}
            QPushButton {{
                background-color: {COLOR_BACKGROUND_ALT};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_SURFACE};
            }}
            QDialogButtonBox QPushButton {{
                min-width: 80px;
            }}
        """)

        layout = QVBoxLayout(self)

        # Ollama Settings
        ollama_group = QGroupBox("Ollama Configuration")
        ollama_layout = QVBoxLayout(ollama_group)

        # Endpoint
        endpoint_layout = QHBoxLayout()
        endpoint_layout.addWidget(QLabel("Endpoint:"))
        self.endpoint_input = QLineEdit()
        self.endpoint_input.setPlaceholderText("http://localhost:11434")
        endpoint_layout.addWidget(self.endpoint_input)
        ollama_layout.addLayout(endpoint_layout)

        # Model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_input = QComboBox()
        self.model_input.setEditable(True)
        self.model_input.addItems(['llama3.2', 'llama3.1', 'mistral', 'mixtral', 'phi3', 'gemma2'])
        model_layout.addWidget(self.model_input)
        ollama_layout.addLayout(model_layout)

        # Test connection button
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        self.test_status = QLabel("")
        test_layout.addWidget(self.test_btn)
        test_layout.addWidget(self.test_status)
        test_layout.addStretch()
        ollama_layout.addLayout(test_layout)

        layout.addWidget(ollama_group)

        # App Settings
        app_group = QGroupBox("Application Settings")
        app_layout = QVBoxLayout(app_group)

        # Default save path
        save_layout = QHBoxLayout()
        save_layout.addWidget(QLabel("Default Save Location:"))
        self.save_path_input = QLineEdit()
        self.save_path_input.setReadOnly(True)
        save_layout.addWidget(self.save_path_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_save_path)
        save_layout.addWidget(browse_btn)
        app_layout.addLayout(save_layout)

        # Default grade level
        grade_layout = QHBoxLayout()
        grade_layout.addWidget(QLabel("Default Grade Level:"))
        self.grade_combo = QComboBox()
        self.grade_combo.addItems(['', 'K-2', '3-5', '6-8', '9-12', 'Higher Ed'])
        grade_layout.addWidget(self.grade_combo)
        grade_layout.addStretch()
        app_layout.addLayout(grade_layout)

        layout.addWidget(app_group)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_settings(self):
        prefs = self.storage.get_preferences()
        self.endpoint_input.setText(prefs.get('ollama_endpoint', 'http://localhost:11434'))
        self.model_input.setCurrentText(prefs.get('ollama_model', 'llama3.2'))
        self.save_path_input.setText(prefs.get('default_save_path', ''))

        grade = prefs.get('default_grade_level', '')
        index = self.grade_combo.findText(grade)
        if index >= 0:
            self.grade_combo.setCurrentIndex(index)

    def save_settings(self):
        prefs = self.storage.get_preferences()
        prefs['ollama_endpoint'] = self.endpoint_input.text() or 'http://localhost:11434'
        prefs['ollama_model'] = self.model_input.currentText() or 'llama3.2'
        prefs['default_save_path'] = self.save_path_input.text()
        prefs['default_grade_level'] = self.grade_combo.currentText()
        self.storage.save_preferences(prefs)
        self.accept()

    def browse_save_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Default Save Location")
        if path:
            self.save_path_input.setText(path)

    def test_connection(self):
        self.test_status.setText("Testing...")
        self.test_status.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        self.test_btn.setEnabled(False)

        endpoint = self.endpoint_input.text() or 'http://localhost:11434'
        ollama = OllamaService(endpoint)
        success, message, models = ollama.test_connection()

        if success and models:
            self.test_status.setText(f"✓ {message}")
            self.test_status.setStyleSheet(f"color: {COLOR_SUCCESS};")
            # Update model dropdown with available models
            current = self.model_input.currentText()
            self.model_input.clear()
            self.model_input.addItems(models)
            if current in models:
                self.model_input.setCurrentText(current)
        else:
            self.test_status.setText(f"✗ {message}")
            self.test_status.setStyleSheet(f"color: {COLOR_ERROR};")

        self.test_btn.setEnabled(True)


# ============================================================================
# Tutorial Dialog
# ============================================================================

class TutorialDialog(QDialog):
    """Tutorial dialog that walks users through the wizard steps (5th grade reading level)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 0
        self.setup_ui()

    def setup_ui(self):
        """Set up the tutorial dialog UI."""
        self.setWindowTitle("How to Use the Wizard")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR_BACKGROUND};
            }}
            QLabel {{
                color: {COLOR_TEXT_PRIMARY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        self.title_label = QLabel()
        self.title_label.setFont(QFont('', 18, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {COLOR_PRIMARY};")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Content area with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLOR_SURFACE};
                border-radius: 8px;
            }}
        """)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(16, 16, 16, 16)

        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet(f"""
            font-size: 14px;
            line-height: 1.6;
            color: {COLOR_TEXT_PRIMARY};
        """)
        self.content_layout.addWidget(self.content_label)
        self.content_layout.addStretch()

        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll, 1)

        # Progress indicator
        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(self.progress_label)

        # Navigation buttons
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("← Back")
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BACKGROUND_ALT};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_SURFACE};
            }}
        """)
        nav_layout.addWidget(self.prev_btn)

        nav_layout.addStretch()

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_DARK};
            }}
        """)
        nav_layout.addWidget(self.next_btn)

        layout.addLayout(nav_layout)

        # Load tutorial content
        self.load_tutorial_content()
        self.show_page(0)

    def load_tutorial_content(self):
        """Load the tutorial pages - written at 5th grade reading level."""
        self.pages = [
            {
                "title": "Welcome to the Tutorial!",
                "content": """<p><b>Hi there!</b> This guide will show you how to use the Assignment Wizard.</p>

<p>The wizard helps teachers make different versions of the same lesson. This way, all students can learn the same thing, but in a way that works best for them!</p>

<p><b>What you will learn:</b></p>
<ul>
<li>How to tell the wizard what you want students to learn</li>
<li>How to describe your students' needs</li>
<li>How to make the best learning materials</li>
<li>How to save and share your work</li>
</ul>

<p>Click <b>Next</b> to start learning!</p>"""
            },
            {
                "title": "Step 1: Learning Objective",
                "content": """<p><b>What is a Learning Objective?</b></p>
<p>A learning objective tells us what students should know or be able to do after the lesson.</p>

<p><b>How to write a good objective:</b></p>
<ul>
<li>Start with "Students will be able to..."</li>
<li>Use action words like: identify, explain, create, compare, solve</li>
<li>Be specific about what they will learn</li>
</ul>

<p><b>Example:</b><br>
"Students will be able to find the main idea in a story and tell why it is important."</p>

<p><b>Don't forget to:</b></p>
<ul>
<li>Pick the right grade level (K-2, 3-5, 6-8, 9-12, or Higher Ed)</li>
<li>Write the subject if you want (like Math or Science)</li>
</ul>"""
            },
            {
                "title": "Step 2: Student Needs",
                "content": """<p><b>Every student is different!</b></p>
<p>This step helps you tell the wizard about your students so it can make materials that work for everyone.</p>

<p><b>Things to think about:</b></p>
<ul>
<li>Do some students need extra help with reading?</li>
<li>Are some students learning English?</li>
<li>Do some students need more of a challenge?</li>
<li>Do some students learn better with pictures?</li>
</ul>

<p><b>Example:</b><br>
"I have 3 students with reading support, 5 students learning English, and 2 students who need harder work. Some students like to work in groups."</p>

<p>The more you tell the wizard, the better it can help!</p>"""
            },
            {
                "title": "Step 3: UDL Framework",
                "content": """<p><b>UDL stands for Universal Design for Learning.</b></p>
<p>It's a fancy way of saying we should teach in many different ways!</p>

<p><b>The three parts of UDL:</b></p>

<p><b>1. Engagement (The WHY)</b><br>
How will you make students excited to learn?<br>
<i>Example: Let students pick topics they like, work with friends, or connect to real life.</i></p>

<p><b>2. Representation (The WHAT)</b><br>
How will you show the information?<br>
<i>Example: Use videos, pictures, read aloud, hands-on activities.</i></p>

<p><b>3. Action & Expression (The HOW)</b><br>
How will students show what they learned?<br>
<i>Example: Write a story, draw a picture, make a video, give a speech.</i></p>

<p><i>This step is optional, but it helps a lot!</i></p>"""
            },
            {
                "title": "Step 4: Resources",
                "content": """<p><b>What tools do you have?</b></p>
<p>Tell the wizard what technology and materials you can use.</p>

<p><b>Technology examples:</b></p>
<ul>
<li>Google Classroom or Canvas</li>
<li>iPads or computers</li>
<li>Smart board</li>
<li>Learning apps like Kahoot or Nearpod</li>
</ul>

<p><b>Materials examples:</b></p>
<ul>
<li>Textbooks and workbooks</li>
<li>Art supplies</li>
<li>Blocks or other hands-on tools</li>
<li>Posters and charts</li>
</ul>

<p>The wizard uses this info to make sure your materials work with what you have!</p>

<p><i>This step is optional.</i></p>"""
            },
            {
                "title": "Step 5: Student Interests",
                "content": """<p><b>What do your students like?</b></p>
<p>When lessons include things students care about, they pay more attention and learn better!</p>

<p><b>Think about:</b></p>
<ul>
<li>Favorite games (Minecraft, Roblox, sports)</li>
<li>TV shows or movies they like</li>
<li>Hobbies (art, music, animals)</li>
<li>Things they talk about at lunch</li>
</ul>

<p><b>Example:</b><br>
"My students love soccer, Minecraft, and animals. They also like TikTok and cooking shows."</p>

<p>The wizard can use these interests to make learning more fun!</p>

<p><i>This step is optional.</i></p>"""
            },
            {
                "title": "Step 6: AI Chat",
                "content": """<p><b>Talk to the AI helper!</b></p>
<p>This step lets you chat with the computer to make your lesson even better.</p>

<p><b>What you can do:</b></p>
<ul>
<li>Ask questions about your lesson plan</li>
<li>Get ideas for how to teach something</li>
<li>Ask for help making things clearer</li>
</ul>

<p><b>How to use it:</b></p>
<ol>
<li>Click "Start Conversation"</li>
<li>Read what the AI suggests</li>
<li>Type your questions or ideas</li>
<li>Click "Send" to get an answer</li>
</ol>

<p>You can skip this step if you want - it's just here to help!</p>

<p><i>This step is optional.</i></p>"""
            },
            {
                "title": "Step 7: Generate Materials",
                "content": """<p><b>Time to create your lessons!</b></p>
<p>Click the big button to make all your differentiated materials.</p>

<p><b>The wizard creates 5 different versions:</b></p>
<ol>
<li><b>Simplified</b> - Easier words and shorter sentences</li>
<li><b>On-Level</b> - Just right for grade level</li>
<li><b>Enriched</b> - More challenging for advanced students</li>
<li><b>Visual-Heavy</b> - Lots of pictures and diagrams</li>
<li><b>Scaffolded</b> - Step-by-step instructions</li>
</ol>

<p><b>After creating:</b></p>
<ul>
<li>Click tabs to see each version</li>
<li>Export as Word, PDF, or PowerPoint</li>
<li>Click "Save to Dashboard" to keep it for later</li>
</ul>

<p>That's it - you did it!</p>"""
            },
            {
                "title": "You're Ready!",
                "content": """<p><b>Great job learning the wizard!</b></p>

<p><b>Quick tips to remember:</b></p>
<ul>
<li>Steps 1 and 2 are required - the rest are optional but helpful</li>
<li>The more details you give, the better your materials will be</li>
<li>Save your work to the Dashboard to use it again later</li>
<li>You can rename or delete assignments on the Dashboard</li>
</ul>

<p><b>Need help?</b></p>
<ul>
<li>Click this Tutorial button anytime to review</li>
<li>Hover over things to see helpful tips</li>
<li>Ask your tech support team if you get stuck</li>
</ul>

<p>Click <b>Finish</b> to close this guide and start making great lessons!</p>"""
            }
        ]

    def show_page(self, page_num):
        """Display a specific tutorial page."""
        if 0 <= page_num < len(self.pages):
            self.current_page = page_num
            page = self.pages[page_num]
            self.title_label.setText(page["title"])
            self.content_label.setText(page["content"])

            # Update progress
            self.progress_label.setText(f"Page {page_num + 1} of {len(self.pages)}")

            # Update navigation buttons
            self.prev_btn.setEnabled(page_num > 0)
            if page_num == len(self.pages) - 1:
                self.next_btn.setText("Finish")
            else:
                self.next_btn.setText("Next →")

    def next_page(self):
        """Go to next page or close dialog."""
        if self.current_page < len(self.pages) - 1:
            self.show_page(self.current_page + 1)
        else:
            self.accept()

    def prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.show_page(self.current_page - 1)


# ============================================================================
# Wizard Step Widgets
# ============================================================================

class StepObjective(QWidget):
    """Step 1: Learning Objective"""

    def __init__(self, form_data: dict):
        super().__init__()
        self.form_data = form_data
        self._loading = False  # Flag to prevent update_form during load
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Step 1: Define Your Learning Objective")
        title.setFont(QFont('', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel("What should students know or be able to do by the end of the lesson?")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Learning objective
        layout.addWidget(QLabel("Learning Objective: *"))
        self.objective_input = QTextEdit()
        self.objective_input.setPlaceholderText(
            "Example: Students will be able to identify the main idea and supporting details "
            "in an informational text and explain how they contribute to the author's purpose."
        )
        self.objective_input.setMaximumHeight(100)
        self.objective_input.textChanged.connect(self.update_form)
        layout.addWidget(self.objective_input)

        # Grade level
        grade_layout = QHBoxLayout()
        grade_layout.addWidget(QLabel("Grade Level: *"))
        self.grade_combo = QComboBox()
        self.grade_combo.setView(QListView())  # Explicit view for macOS compatibility
        self.grade_combo.setMinimumWidth(120)
        self.grade_combo.addItems(['Select...', 'K-2', '3-5', '6-8', '9-12', 'Higher Ed'])
        self.grade_combo.currentTextChanged.connect(self.update_form)
        grade_layout.addWidget(self.grade_combo)
        grade_layout.addStretch()
        layout.addLayout(grade_layout)

        # Subject
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("Subject (optional):"))
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("e.g., English Language Arts, Science, Math")
        self.subject_input.textChanged.connect(self.update_form)
        subject_layout.addWidget(self.subject_input)
        layout.addLayout(subject_layout)

        layout.addStretch()

    def update_form(self):
        if self._loading:
            return  # Skip updates while loading data
        self.form_data['learning_objective'] = self.objective_input.toPlainText()
        grade = self.grade_combo.currentText()
        self.form_data['grade_level'] = '' if grade == 'Select...' else grade
        self.form_data['subject'] = self.subject_input.text()

    def load_data(self):
        self._loading = True
        self.objective_input.setPlainText(self.form_data.get('learning_objective', ''))
        grade = self.form_data.get('grade_level', '')
        index = self.grade_combo.findText(grade) if grade else 0
        self.grade_combo.setCurrentIndex(max(0, index))
        self.subject_input.setText(self.form_data.get('subject', ''))
        self._loading = False

    def validate(self) -> tuple[bool, str]:
        if not self.form_data.get('learning_objective', '').strip():
            return False, "Please enter a learning objective."
        if not self.form_data.get('grade_level'):
            return False, "Please select a grade level."
        return True, ""


class StepNeeds(QWidget):
    """Step 2: Student Needs"""

    def __init__(self, form_data: dict):
        super().__init__()
        self.form_data = form_data
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Step 2: Describe Student Learning Needs")
        title.setFont(QFont('', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel(
            "Describe the diverse learning needs in your classroom. Consider students with "
            "different abilities, learning styles, language backgrounds, and any specific "
            "accommodations or modifications needed."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addWidget(QLabel("Student Needs: *"))
        self.needs_input = QTextEdit()
        self.needs_input.setPlaceholderText(
            "Example: My class includes 3 students with IEPs for reading comprehension, "
            "5 English Language Learners at intermediate proficiency, 2 students who are "
            "above grade level and need enrichment, and several students who benefit from "
            "visual supports and graphic organizers."
        )
        self.needs_input.textChanged.connect(self.update_form)
        layout.addWidget(self.needs_input)

        layout.addStretch()

    def update_form(self):
        self.form_data['student_needs'] = self.needs_input.toPlainText()

    def load_data(self):
        self.needs_input.setPlainText(self.form_data.get('student_needs', ''))

    def validate(self) -> tuple[bool, str]:
        if not self.form_data.get('student_needs', '').strip():
            return False, "Please describe your students' learning needs."
        return True, ""


class StepUDL(QWidget):
    """Step 3: UDL Framework"""

    def __init__(self, form_data: dict):
        super().__init__()
        self.form_data = form_data
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Step 3: UDL Framework Considerations")
        title.setFont(QFont('', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel(
            "Universal Design for Learning (UDL) provides a framework for creating flexible "
            "learning experiences. Consider how you'll address each principle. (All optional)"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Engagement
        engage_group = QGroupBox("Engagement (The 'Why' of Learning)")
        engage_layout = QVBoxLayout(engage_group)
        engage_desc = QLabel("How will you motivate and sustain student interest?")
        engage_desc.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        engage_layout.addWidget(engage_desc)
        self.engagement_input = QTextEdit()
        self.engagement_input.setPlaceholderText(
            "e.g., Choice in topics, collaborative activities, real-world connections..."
        )
        self.engagement_input.setMaximumHeight(80)
        self.engagement_input.textChanged.connect(self.update_form)
        engage_layout.addWidget(self.engagement_input)
        layout.addWidget(engage_group)

        # Representation
        rep_group = QGroupBox("Representation (The 'What' of Learning)")
        rep_layout = QVBoxLayout(rep_group)
        rep_desc = QLabel("How will you present information in multiple ways?")
        rep_desc.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        rep_layout.addWidget(rep_desc)
        self.representation_input = QTextEdit()
        self.representation_input.setPlaceholderText(
            "e.g., Videos, diagrams, audio explanations, hands-on materials..."
        )
        self.representation_input.setMaximumHeight(80)
        self.representation_input.textChanged.connect(self.update_form)
        rep_layout.addWidget(self.representation_input)
        layout.addWidget(rep_group)

        # Expression
        exp_group = QGroupBox("Action & Expression (The 'How' of Learning)")
        exp_layout = QVBoxLayout(exp_group)
        exp_desc = QLabel("How will students demonstrate their learning?")
        exp_desc.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        exp_layout.addWidget(exp_desc)
        self.expression_input = QTextEdit()
        self.expression_input.setPlaceholderText(
            "e.g., Written response, oral presentation, drawing, digital creation..."
        )
        self.expression_input.setMaximumHeight(80)
        self.expression_input.textChanged.connect(self.update_form)
        exp_layout.addWidget(self.expression_input)
        layout.addWidget(exp_group)

        layout.addStretch()

    def update_form(self):
        self.form_data['engagement'] = self.engagement_input.toPlainText()
        self.form_data['representation'] = self.representation_input.toPlainText()
        self.form_data['expression'] = self.expression_input.toPlainText()

    def load_data(self):
        self.engagement_input.setPlainText(self.form_data.get('engagement', ''))
        self.representation_input.setPlainText(self.form_data.get('representation', ''))
        self.expression_input.setPlainText(self.form_data.get('expression', ''))

    def validate(self) -> tuple[bool, str]:
        return True, ""  # Optional step


class StepResources(QWidget):
    """Step 4: Available Resources"""

    def __init__(self, form_data: dict):
        super().__init__()
        self.form_data = form_data
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Step 4: Available Platforms & Resources")
        title.setFont(QFont('', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel(
            "What technology platforms, materials, and resources do you have available? "
            "This helps generate materials that fit your context. (Optional)"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Platforms
        layout.addWidget(QLabel("Technology Platforms:"))
        self.platforms_input = QTextEdit()
        self.platforms_input.setPlaceholderText(
            "e.g., Google Classroom, Canvas, Nearpod, Kahoot, student iPads, "
            "interactive whiteboard, document camera..."
        )
        self.platforms_input.setMaximumHeight(100)
        self.platforms_input.textChanged.connect(self.update_form)
        layout.addWidget(self.platforms_input)

        # Resources
        layout.addWidget(QLabel("Physical Resources & Materials:"))
        self.resources_input = QTextEdit()
        self.resources_input.setPlaceholderText(
            "e.g., Textbooks, manipulatives, art supplies, science lab equipment, "
            "anchor charts, leveled readers..."
        )
        self.resources_input.setMaximumHeight(100)
        self.resources_input.textChanged.connect(self.update_form)
        layout.addWidget(self.resources_input)

        layout.addStretch()

    def update_form(self):
        self.form_data['platforms'] = self.platforms_input.toPlainText()
        self.form_data['resources'] = self.resources_input.toPlainText()

    def load_data(self):
        self.platforms_input.setPlainText(self.form_data.get('platforms', ''))
        self.resources_input.setPlainText(self.form_data.get('resources', ''))

    def validate(self) -> tuple[bool, str]:
        return True, ""  # Optional step


class StepInterests(QWidget):
    """Step 5: Student Interests"""

    def __init__(self, form_data: dict):
        super().__init__()
        self.form_data = form_data
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Step 5: Student Interests")
        title.setFont(QFont('', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel(
            "What are your students interested in? Incorporating student interests "
            "increases engagement and makes learning more meaningful. (Optional)"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addWidget(QLabel("Student Interests:"))
        self.interests_input = QTextEdit()
        self.interests_input.setPlaceholderText(
            "e.g., Sports (especially soccer and basketball), video games (Minecraft, Roblox), "
            "animals, music, TikTok trends, superheroes, cooking shows..."
        )
        self.interests_input.setMaximumHeight(120)
        self.interests_input.textChanged.connect(self.update_form)
        layout.addWidget(self.interests_input)

        layout.addWidget(QLabel("How did you gather this information? (optional)"))
        self.evidence_input = QTextEdit()
        self.evidence_input.setPlaceholderText(
            "e.g., Interest surveys, classroom conversations, observation..."
        )
        self.evidence_input.setMaximumHeight(80)
        self.evidence_input.textChanged.connect(self.update_form)
        layout.addWidget(self.evidence_input)

        layout.addStretch()

    def update_form(self):
        self.form_data['interests'] = self.interests_input.toPlainText()
        self.form_data['interests_evidence'] = self.evidence_input.toPlainText()

    def load_data(self):
        self.interests_input.setPlainText(self.form_data.get('interests', ''))
        self.evidence_input.setPlainText(self.form_data.get('interests_evidence', ''))

    def validate(self) -> tuple[bool, str]:
        return True, ""  # Optional step


class StepConversation(QWidget):
    """Step 6: AI Conversation for Refinement"""

    def __init__(self, form_data: dict, ollama: OllamaService):
        super().__init__()
        self.form_data = form_data
        self.ollama = ollama
        self.messages = []
        self.chat_worker = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Step 6: Refine with AI (Optional)")
        title.setFont(QFont('', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel(
            "Chat with the AI to refine your inputs and get suggestions. "
            "This step is optional - you can proceed directly to generation."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText(
            "Click 'Start Conversation' to get AI suggestions for improving your materials..."
        )
        layout.addWidget(self.chat_display, 1)

        # Input area
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setEnabled(False)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)

        # Start conversation button
        self.start_btn = QPushButton("Start Conversation")
        self.start_btn.clicked.connect(self.start_conversation)
        layout.addWidget(self.start_btn)

    def start_conversation(self):
        self.messages = []
        self.chat_display.clear()
        self.start_btn.setEnabled(False)
        self.append_message("system", "Starting conversation with AI assistant...")

        # Create initial prompt asking for suggestions
        initial_prompt = (
            "I'm creating differentiated learning materials. Based on what I've provided so far, "
            "please ask me clarifying questions or offer suggestions to improve the materials. "
            "Keep your response concise."
        )
        self.messages.append({"role": "user", "content": initial_prompt})

        system_prompt = build_conversation_prompt(self.form_data)
        self.chat_worker = ChatWorker(self.ollama, self.messages, system_prompt)
        self.chat_worker.response_chunk.connect(self.on_response_chunk)
        self.chat_worker.finished.connect(self.on_response_complete)
        self.chat_worker.error.connect(self.on_chat_error)
        self.chat_worker.start()

    def send_message(self):
        message = self.message_input.text().strip()
        if not message:
            return

        self.message_input.clear()
        self.send_btn.setEnabled(False)
        self.append_message("user", message)

        self.messages.append({"role": "user", "content": message})

        system_prompt = build_conversation_prompt(self.form_data)
        self.chat_worker = ChatWorker(self.ollama, self.messages, system_prompt)
        self.chat_worker.response_chunk.connect(self.on_response_chunk)
        self.chat_worker.finished.connect(self.on_response_complete)
        self.chat_worker.error.connect(self.on_chat_error)
        self.chat_worker.start()

    def on_response_chunk(self, chunk: str):
        # Append streaming response
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(chunk)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def on_response_complete(self, response: str):
        self.messages.append({"role": "assistant", "content": response})
        self.chat_display.append("")  # New line after response
        self.send_btn.setEnabled(True)
        self.start_btn.setEnabled(True)

    def on_chat_error(self, error: str):
        self.append_message("system", f"Error: {error}")
        self.send_btn.setEnabled(True)
        self.start_btn.setEnabled(True)

    def append_message(self, role: str, content: str):
        if role == "user":
            self.chat_display.append(f"\n**You:** {content}\n")
        elif role == "assistant":
            self.chat_display.append(f"\n**AI:** ")
        else:
            self.chat_display.append(f"\n*{content}*\n")

    def load_data(self):
        pass  # Conversation doesn't persist

    def validate(self) -> tuple[bool, str]:
        return True, ""  # Optional step


class StepGenerate(QWidget):
    """Step 7: Generate Materials"""

    def __init__(self, form_data: dict, ollama: OllamaService, storage: StorageService):
        super().__init__()
        self.form_data = form_data
        self.ollama = ollama
        self.storage = storage
        self.materials = {}
        self.generation_worker = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Step 7: Generate Differentiated Materials")
        title.setFont(QFont('', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Progress area
        self.progress_group = QGroupBox("Generation Progress")
        progress_layout = QVBoxLayout(self.progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 5)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("Click 'Generate All Materials' to begin")
        progress_layout.addWidget(self.progress_label)

        layout.addWidget(self.progress_group)

        # Generate button
        self.generate_btn = QPushButton("Generate All Materials")
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.clicked.connect(self.start_generation)
        layout.addWidget(self.generate_btn)

        # Results area with tabs
        self.results_tabs = QTabWidget()
        self.result_widgets = {}

        for version_key, version_name in VERSION_NAMES.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            # Content display
            content_display = QTextEdit()
            content_display.setReadOnly(True)
            content_display.setPlaceholderText(f"Content for {version_name} will appear here after generation...")
            tab_layout.addWidget(content_display)

            # Export buttons
            export_layout = QHBoxLayout()
            export_layout.addStretch()

            docx_btn = QPushButton("Export DOCX")
            docx_btn.clicked.connect(partial(self.export_material, version_key, 'docx'))
            docx_btn.setEnabled(False)
            export_layout.addWidget(docx_btn)

            pdf_btn = QPushButton("Export PDF")
            pdf_btn.clicked.connect(partial(self.export_material, version_key, 'pdf'))
            pdf_btn.setEnabled(False)
            export_layout.addWidget(pdf_btn)

            pptx_btn = QPushButton("Export PPTX")
            pptx_btn.clicked.connect(partial(self.export_material, version_key, 'pptx'))
            pptx_btn.setEnabled(False)
            export_layout.addWidget(pptx_btn)

            tab_layout.addLayout(export_layout)

            self.results_tabs.addTab(tab, version_name.split('(')[0].strip())
            self.result_widgets[version_key] = {
                'content': content_display,
                'docx_btn': docx_btn,
                'pdf_btn': pdf_btn,
                'pptx_btn': pptx_btn
            }

        layout.addWidget(self.results_tabs, 1)

        # Bottom buttons row
        bottom_layout = QHBoxLayout()

        # Save to Dashboard button
        self.save_dashboard_btn = QPushButton("Save to Dashboard")
        self.save_dashboard_btn.clicked.connect(self.save_to_dashboard)
        self.save_dashboard_btn.setEnabled(False)
        bottom_layout.addWidget(self.save_dashboard_btn)

        bottom_layout.addStretch()

        # Export all button
        self.export_all_btn = QPushButton("Export All to Excel")
        self.export_all_btn.clicked.connect(self.export_all_xlsx)
        self.export_all_btn.setEnabled(False)
        bottom_layout.addWidget(self.export_all_btn)

        layout.addLayout(bottom_layout)

        # Callback for saving to dashboard (set by MainWindow)
        self.save_to_dashboard_requested = None

    def start_generation(self):
        # Validate required data
        if not self.form_data.get('learning_objective'):
            QMessageBox.warning(self, "Missing Data", "Please complete the learning objective in Step 1.")
            return
        if not self.form_data.get('grade_level'):
            QMessageBox.warning(self, "Missing Data", "Please select a grade level in Step 1.")
            return
        if not self.form_data.get('student_needs'):
            QMessageBox.warning(self, "Missing Data", "Please describe student needs in Step 2.")
            return

        self.generate_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting generation...")
        self.materials = {}

        # Clear previous results
        for widgets in self.result_widgets.values():
            widgets['content'].clear()
            widgets['docx_btn'].setEnabled(False)
            widgets['pdf_btn'].setEnabled(False)
            widgets['pptx_btn'].setEnabled(False)
        self.export_all_btn.setEnabled(False)
        self.save_dashboard_btn.setEnabled(False)

        self.generation_worker = GenerationWorker(self.ollama, self.form_data)
        self.generation_worker.progress.connect(self.on_generation_progress)
        self.generation_worker.version_complete.connect(self.on_version_complete)
        self.generation_worker.finished.connect(self.on_generation_finished)
        self.generation_worker.start()

    def on_generation_progress(self, version_key: str, percentage: int):
        version_name = VERSION_NAMES.get(version_key, version_key)
        if percentage == 0:
            self.progress_label.setText(f"Generating {version_name}...")

    def on_version_complete(self, version_key: str, result: dict):
        self.materials[version_key] = result
        self.progress_bar.setValue(len(self.materials))

        widgets = self.result_widgets.get(version_key)
        if widgets:
            if result.get('error'):
                widgets['content'].setPlainText(f"Error: {result['error']}")
            else:
                widgets['content'].setPlainText(result.get('content', ''))
                widgets['docx_btn'].setEnabled(True)
                widgets['pdf_btn'].setEnabled(True)
                widgets['pptx_btn'].setEnabled(True)

    def on_generation_finished(self, results: dict):
        self.materials = results
        self.generate_btn.setEnabled(True)
        self.progress_label.setText("Generation complete!")
        self.export_all_btn.setEnabled(True)
        self.save_dashboard_btn.setEnabled(True)

    def export_material(self, version_key: str, format_type: str):
        if version_key not in self.materials:
            return

        prefs = self.storage.get_preferences()
        default_path = prefs.get('default_save_path', str(os.path.expanduser('~/Desktop')))

        save_path = QFileDialog.getExistingDirectory(
            self, "Select Save Location", default_path
        )
        if not save_path:
            return

        try:
            if format_type == 'docx':
                filepath = export_to_docx(self.materials, self.form_data, version_key, save_path)
            elif format_type == 'pdf':
                filepath = export_to_pdf(self.materials, self.form_data, version_key, save_path)
            elif format_type == 'pptx':
                filepath = export_to_pptx(self.materials, self.form_data, version_key, save_path)
            else:
                return

            QMessageBox.information(
                self, "Export Complete",
                f"File saved to:\n{filepath}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")

    def export_all_xlsx(self):
        if not self.materials:
            return

        prefs = self.storage.get_preferences()
        default_path = prefs.get('default_save_path', str(os.path.expanduser('~/Desktop')))

        save_path = QFileDialog.getExistingDirectory(
            self, "Select Save Location", default_path
        )
        if not save_path:
            return

        try:
            filepath = export_all_to_xlsx(self.materials, self.form_data, save_path)
            QMessageBox.information(
                self, "Export Complete",
                f"Excel file saved to:\n{filepath}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")

    def save_to_dashboard(self):
        """Save the current assignment to the dashboard."""
        if not self.materials:
            return

        # Get assignment name from user
        objective = self.form_data.get('learning_objective', '')[:50]
        default_name = objective if objective else "Untitled Assignment"

        name, ok = QInputDialog.getText(
            self, "Save to Dashboard",
            "Enter a name for this assignment:",
            QLineEdit.EchoMode.Normal,
            default_name
        )

        if ok and name:
            if self.save_to_dashboard_requested:
                self.save_to_dashboard_requested(name, self.materials.copy())

    def load_data(self):
        pass  # Results don't persist

    def validate(self) -> tuple[bool, str]:
        return True, ""


# ============================================================================
# Dashboard Widget
# ============================================================================

class DashboardWidget(QWidget):
    """Dashboard for viewing and managing saved assignments."""

    # Signal emitted when user wants to load an assignment into the wizard
    load_assignment_requested = pyqtSignal(dict)
    back_to_wizard_requested = pyqtSignal()

    def __init__(self, storage: StorageService):
        super().__init__()
        self.storage = storage
        self.current_assignment = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Use stacked widget to switch between list and detail views
        self.view_stack = QStackedWidget()

        # === List View (index 0) ===
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)

        # Header
        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Back to Wizard")
        back_btn.clicked.connect(self.back_to_wizard_requested.emit)
        header_layout.addWidget(back_btn)
        header_layout.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search assignments...")
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self.filter_assignments)
        header_layout.addWidget(self.search_input)
        list_layout.addLayout(header_layout)

        # Title
        title_label = QLabel("Saved Assignments")
        title_label.setFont(QFont('', 18, QFont.Weight.Bold))
        list_layout.addWidget(title_label)

        # Assignment list
        self.assignment_list = QListWidget()
        self.assignment_list.setSpacing(5)
        self.assignment_list.itemDoubleClicked.connect(self.view_assignment_from_item)
        list_layout.addWidget(self.assignment_list, 1)

        # Empty state message
        self.empty_label = QLabel("No saved assignments yet.\n\nGenerate materials in the wizard and click 'Save to Dashboard' to save them here.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 14px;")
        list_layout.addWidget(self.empty_label)

        self.view_stack.addWidget(list_widget)

        # === Detail View (index 1) ===
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)

        # Detail header
        detail_header = QHBoxLayout()
        self.back_to_list_btn = QPushButton("← Back to List")
        self.back_to_list_btn.clicked.connect(self.show_list_view)
        detail_header.addWidget(self.back_to_list_btn)
        detail_header.addStretch()

        self.rename_btn = QPushButton("Rename")
        self.rename_btn.clicked.connect(self.rename_current_assignment)
        detail_header.addWidget(self.rename_btn)

        self.load_into_wizard_btn = QPushButton("Load into Wizard")
        self.load_into_wizard_btn.clicked.connect(self.load_current_into_wizard)
        detail_header.addWidget(self.load_into_wizard_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet(f"color: {COLOR_ERROR};")
        self.delete_btn.clicked.connect(self.delete_current_assignment)
        detail_header.addWidget(self.delete_btn)
        detail_layout.addLayout(detail_header)

        # Assignment info
        self.detail_title = QLabel()
        self.detail_title.setFont(QFont('', 16, QFont.Weight.Bold))
        detail_layout.addWidget(self.detail_title)

        self.detail_info = QLabel()
        self.detail_info.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        detail_layout.addWidget(self.detail_info)

        # Learning objective
        obj_group = QGroupBox("Learning Objective")
        obj_layout = QVBoxLayout(obj_group)
        self.objective_display = QLabel()
        self.objective_display.setWordWrap(True)
        obj_layout.addWidget(self.objective_display)
        detail_layout.addWidget(obj_group)

        # Generated content tabs
        content_group = QGroupBox("Generated Versions")
        content_layout = QVBoxLayout(content_group)

        self.content_tabs = QTabWidget()
        self.content_displays = {}

        for version_key, version_name in VERSION_NAMES.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            content_display = QTextEdit()
            content_display.setReadOnly(True)
            tab_layout.addWidget(content_display)

            # Export buttons
            export_layout = QHBoxLayout()
            export_layout.addStretch()

            docx_btn = QPushButton("Export DOCX")
            docx_btn.clicked.connect(partial(self.export_material, version_key, 'docx'))
            export_layout.addWidget(docx_btn)

            pdf_btn = QPushButton("Export PDF")
            pdf_btn.clicked.connect(partial(self.export_material, version_key, 'pdf'))
            export_layout.addWidget(pdf_btn)

            pptx_btn = QPushButton("Export PPTX")
            pptx_btn.clicked.connect(partial(self.export_material, version_key, 'pptx'))
            export_layout.addWidget(pptx_btn)

            tab_layout.addLayout(export_layout)

            self.content_tabs.addTab(tab, version_name.split('(')[0].strip())
            self.content_displays[version_key] = content_display

        content_layout.addWidget(self.content_tabs)
        detail_layout.addWidget(content_group, 1)

        # Reflections section
        reflections_group = QGroupBox("Reflections")
        reflections_layout = QVBoxLayout(reflections_group)

        # What worked well
        reflections_layout.addWidget(QLabel("What worked well and why:"))
        self.worked_well_input = QTextEdit()
        self.worked_well_input.setMaximumHeight(80)
        self.worked_well_input.setPlaceholderText("Describe what was effective about this lesson...")
        reflections_layout.addWidget(self.worked_well_input)

        # What did not work
        reflections_layout.addWidget(QLabel("What did not work well and why:"))
        self.did_not_work_input = QTextEdit()
        self.did_not_work_input.setMaximumHeight(80)
        self.did_not_work_input.setPlaceholderText("Describe challenges or issues encountered...")
        reflections_layout.addWidget(self.did_not_work_input)

        # What could be better
        reflections_layout.addWidget(QLabel("What could be better next time:"))
        self.could_be_better_input = QTextEdit()
        self.could_be_better_input.setMaximumHeight(80)
        self.could_be_better_input.setPlaceholderText("Ideas for improvement...")
        reflections_layout.addWidget(self.could_be_better_input)

        # Save reflections button
        save_reflections_btn = QPushButton("Save Reflections")
        save_reflections_btn.clicked.connect(self.save_reflections)
        reflections_layout.addWidget(save_reflections_btn)

        detail_layout.addWidget(reflections_group)

        # Wrap detail view in scroll area
        detail_scroll = QScrollArea()
        detail_scroll.setWidget(detail_widget)
        detail_scroll.setWidgetResizable(True)
        detail_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.view_stack.addWidget(detail_scroll)

        layout.addWidget(self.view_stack)

    def refresh_list(self):
        """Refresh the assignment list from storage."""
        self.assignment_list.clear()
        assignments = self.storage.get_assignments()

        # Sort by updated_at descending (most recent first)
        assignments.sort(key=lambda x: x.get('updated_at', ''), reverse=True)

        self.empty_label.setVisible(len(assignments) == 0)
        self.assignment_list.setVisible(len(assignments) > 0)

        for assignment in assignments:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, assignment['id'])

            # Create rich display text
            name = assignment.get('name', 'Untitled')
            grade = assignment.get('form_data', {}).get('grade_level', 'N/A')
            subject = assignment.get('form_data', {}).get('subject', '') or 'No subject'
            created = assignment.get('created_at', '')[:10]  # Just the date part

            item.setText(f"{name}\nGrade: {grade} | Subject: {subject} | Created: {created}")
            item.setSizeHint(item.sizeHint().expandedTo(QListWidgetItem().sizeHint()))

            self.assignment_list.addItem(item)

    def filter_assignments(self, search_text: str):
        """Filter assignments by search text."""
        search_lower = search_text.lower()
        for i in range(self.assignment_list.count()):
            item = self.assignment_list.item(i)
            item.setHidden(search_lower not in item.text().lower())

    def view_assignment_from_item(self, item: QListWidgetItem):
        """View assignment details when item is double-clicked."""
        assignment_id = item.data(Qt.ItemDataRole.UserRole)
        assignment = self.storage.get_assignment(assignment_id)
        if assignment:
            self.show_assignment_detail(assignment)

    def show_assignment_detail(self, assignment: dict):
        """Display the detail view for an assignment."""
        self.current_assignment = assignment

        # Update header info
        self.detail_title.setText(assignment.get('name', 'Untitled'))

        form_data = assignment.get('form_data', {})
        grade = form_data.get('grade_level', 'N/A')
        subject = form_data.get('subject', '') or 'No subject'
        created = assignment.get('created_at', '')[:10]
        self.detail_info.setText(f"Grade: {grade} | Subject: {subject} | Created: {created}")

        # Learning objective
        self.objective_display.setText(form_data.get('learning_objective', 'No objective specified'))

        # Generated content
        generated = assignment.get('generated_content', {})
        for version_key, display in self.content_displays.items():
            version_data = generated.get(version_key, {})
            content = version_data.get('content', 'No content available')
            display.setPlainText(content)

        # Reflections
        reflections = assignment.get('reflections', {})
        self.worked_well_input.setPlainText(reflections.get('worked_well', ''))
        self.did_not_work_input.setPlainText(reflections.get('did_not_work', ''))
        self.could_be_better_input.setPlainText(reflections.get('could_be_better', ''))

        # Switch to detail view
        self.view_stack.setCurrentIndex(1)

    def show_list_view(self):
        """Return to the list view."""
        self.view_stack.setCurrentIndex(0)
        self.refresh_list()

    def save_reflections(self):
        """Save the current reflections."""
        if not self.current_assignment:
            return

        reflections = {
            'worked_well': self.worked_well_input.toPlainText(),
            'did_not_work': self.did_not_work_input.toPlainText(),
            'could_be_better': self.could_be_better_input.toPlainText()
        }

        success = self.storage.update_assignment_reflections(
            self.current_assignment['id'],
            reflections
        )

        if success:
            QMessageBox.information(self, "Saved", "Reflections saved successfully!")
            # Update local copy
            self.current_assignment['reflections'] = reflections
        else:
            QMessageBox.warning(self, "Error", "Failed to save reflections.")

    def load_current_into_wizard(self):
        """Load the current assignment into the wizard."""
        if not self.current_assignment:
            return

        reply = QMessageBox.question(
            self, "Load Assignment",
            "This will replace your current wizard data. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.load_assignment_requested.emit(self.current_assignment)

    def delete_current_assignment(self):
        """Delete the current assignment."""
        if not self.current_assignment:
            return

        reply = QMessageBox.question(
            self, "Delete Assignment",
            f"Are you sure you want to delete '{self.current_assignment.get('name', 'this assignment')}'?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.storage.delete_assignment(self.current_assignment['id'])
            self.current_assignment = None
            self.show_list_view()

    def rename_current_assignment(self):
        """Rename the current assignment."""
        if not self.current_assignment:
            return

        current_name = self.current_assignment.get('name', 'Untitled')
        new_name, ok = QInputDialog.getText(
            self, "Rename Assignment",
            "Enter a new name for this assignment:",
            QLineEdit.EchoMode.Normal,
            current_name
        )

        if ok and new_name and new_name != current_name:
            success = self.storage.rename_assignment(self.current_assignment['id'], new_name)
            if success:
                self.current_assignment['name'] = new_name
                self.detail_title.setText(new_name)
                QMessageBox.information(self, "Renamed", f"Assignment renamed to '{new_name}'")
            else:
                QMessageBox.warning(self, "Error", "Failed to rename assignment.")

    def export_material(self, version_key: str, format_type: str):
        """Export a specific version to file."""
        if not self.current_assignment:
            return

        generated = self.current_assignment.get('generated_content', {})
        if version_key not in generated:
            return

        prefs = self.storage.get_preferences()
        default_path = prefs.get('default_save_path', str(os.path.expanduser('~/Desktop')))

        save_path = QFileDialog.getExistingDirectory(
            self, "Select Save Location", default_path
        )
        if not save_path:
            return

        try:
            form_data = self.current_assignment.get('form_data', {})
            materials = generated

            if format_type == 'docx':
                filepath = export_to_docx(materials, form_data, version_key, save_path)
            elif format_type == 'pdf':
                filepath = export_to_pdf(materials, form_data, version_key, save_path)
            elif format_type == 'pptx':
                filepath = export_to_pptx(materials, form_data, version_key, save_path)
            else:
                return

            QMessageBox.information(
                self, "Export Complete",
                f"File saved to:\n{filepath}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")


# ============================================================================
# Main Application Window
# ============================================================================

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.storage = StorageService()
        self.auth = AuthService()
        self.form_data = get_default_form_data()
        self.current_user = None

        # Initialize Ollama with saved settings
        prefs = self.storage.get_preferences()
        self.ollama = OllamaService(
            endpoint=prefs.get('ollama_endpoint', 'http://localhost:11434'),
            model=prefs.get('ollama_model', 'llama3.2')
        )

        self.current_step = 0
        self.steps = []

        self.setup_ui()
        self.check_existing_session()

    def setup_ui(self):
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(900, 700)

        # Apply dark theme to the main window
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLOR_BACKGROUND};
            }}
            QWidget {{
                background-color: {COLOR_BACKGROUND};
                color: {COLOR_TEXT_PRIMARY};
            }}
            QLabel {{
                color: {COLOR_TEXT_PRIMARY};
            }}
            QGroupBox {{
                font-weight: bold;
                color: {COLOR_PRIMARY_LIGHT};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QTextEdit {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_TEXT};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 4px;
                padding: 8px;
            }}
            QTextEdit:focus {{
                border: 2px solid {COLOR_INPUT_FOCUS};
            }}
            QLineEdit {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_TEXT};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 4px;
                padding: 8px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_INPUT_FOCUS};
            }}
            QComboBox {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_TEXT};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 4px;
                padding: 8px;
            }}
            QComboBox:focus {{
                border: 2px solid {COLOR_INPUT_FOCUS};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLOR_TEXT_PRIMARY};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_TEXT};
                selection-background-color: {COLOR_PRIMARY};
                selection-color: white;
                border: 1px solid {COLOR_INPUT_BORDER};
            }}
            QProgressBar {{
                background-color: {COLOR_INPUT_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                text-align: center;
                color: {COLOR_TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background-color: {COLOR_PRIMARY};
                border-radius: 3px;
            }}
            QTabWidget::pane {{
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                background-color: {COLOR_BACKGROUND};
                padding: 8px;
            }}
            QTabBar::tab {{
                padding: 8px 16px;
                margin-right: 4px;
                background-color: {COLOR_BACKGROUND_ALT};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                border-bottom: none;
                border-radius: 4px 4px 0 0;
            }}
            QTabBar::tab:selected {{
                background-color: {COLOR_PRIMARY};
                color: white;
            }}
            QScrollArea {{
                border: none;
                background-color: {COLOR_BACKGROUND};
            }}
            QScrollBar:vertical {{
                background-color: {COLOR_BACKGROUND_ALT};
                width: 12px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLOR_BORDER};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar:horizontal {{
                background-color: {COLOR_BACKGROUND_ALT};
                height: 12px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {COLOR_BORDER};
                border-radius: 6px;
                min-width: 20px;
            }}
            QListWidget {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_TEXT};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 4px;
            }}
            QListWidget::item {{
                padding: 8px;
            }}
            QListWidget::item:selected {{
                background-color: {COLOR_PRIMARY};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {COLOR_SURFACE};
            }}
            QFrame[frameShape="4"] {{
                color: {COLOR_BORDER};
            }}
            QMessageBox {{
                background-color: {COLOR_BACKGROUND};
            }}
            QDialog {{
                background-color: {COLOR_BACKGROUND};
            }}
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Top-level stack: Auth vs App
        self.app_stack = QStackedWidget()

        # Auth view (index 0)
        self.auth_widget = AuthStackedWidget(self.auth)
        self.auth_widget.authenticated.connect(self.on_authenticated)
        self.app_stack.addWidget(self.auth_widget)

        # Main app view (index 1)
        self.main_app_widget = QWidget()
        app_layout = QVBoxLayout(self.main_app_widget)
        app_layout.setSpacing(10)
        app_layout.setContentsMargins(20, 20, 20, 20)

        # Header with dark theme
        header_layout = QHBoxLayout()
        title_label = QLabel(APP_NAME)
        title_label.setFont(QFont('', 20, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLOR_PRIMARY}; background: transparent;")
        title_label.setAccessibleName(f"{APP_NAME} main screen")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # User label
        self.user_label = QLabel("")
        self.user_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        header_layout.addWidget(self.user_label)

        # Track navigation buttons for active state management
        self.nav_buttons = []
        self.active_nav_button = None

        self.dashboard_btn = QPushButton("Dashboard")
        self.dashboard_btn.setMinimumHeight(MIN_TOUCH_TARGET)
        self.dashboard_btn.clicked.connect(lambda: self._on_nav_button_clicked(self.dashboard_btn, self.toggle_dashboard))
        self.dashboard_btn.setAccessibleName("Go to dashboard")
        self._style_nav_button(self.dashboard_btn)
        self.nav_buttons.append(self.dashboard_btn)
        header_layout.addWidget(self.dashboard_btn)

        self.wizard_btn = QPushButton("Wizard")
        self.wizard_btn.setMinimumHeight(MIN_TOUCH_TARGET)
        self.wizard_btn.clicked.connect(lambda: self._on_nav_button_clicked(self.wizard_btn, self.show_wizard_view))
        self.wizard_btn.setAccessibleName("Go to wizard")
        self._style_nav_button(self.wizard_btn)
        self.nav_buttons.append(self.wizard_btn)
        header_layout.addWidget(self.wizard_btn)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setMinimumHeight(MIN_TOUCH_TARGET)
        self.reset_btn.clicked.connect(lambda: self._on_nav_button_clicked(self.reset_btn, self.reset_wizard))
        self.reset_btn.setAccessibleName("Reset wizard form")
        self._style_nav_button(self.reset_btn)
        self.nav_buttons.append(self.reset_btn)
        header_layout.addWidget(self.reset_btn)

        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setMinimumHeight(MIN_TOUCH_TARGET)
        self.settings_btn.clicked.connect(lambda: self._on_nav_button_clicked(self.settings_btn, self.open_settings))
        self.settings_btn.setAccessibleName("Open settings")
        self._style_nav_button(self.settings_btn)
        self.nav_buttons.append(self.settings_btn)
        header_layout.addWidget(self.settings_btn)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setMinimumHeight(MIN_TOUCH_TARGET)
        self.logout_btn.clicked.connect(lambda: self._on_nav_button_clicked(self.logout_btn, self.logout))
        self.logout_btn.setAccessibleName("Log out of application")
        self._style_nav_button(self.logout_btn)
        self.nav_buttons.append(self.logout_btn)
        header_layout.addWidget(self.logout_btn)

        # Set initial active button to Wizard
        self._set_active_nav_button(self.wizard_btn)

        app_layout.addLayout(header_layout)

        # Top-level view stack (Wizard vs Dashboard)
        self.main_view_stack = QStackedWidget()

        # === Wizard View (index 0) ===
        wizard_widget = QWidget()
        wizard_layout = QVBoxLayout(wizard_widget)
        wizard_layout.setContentsMargins(0, 0, 0, 0)
        wizard_layout.setSpacing(10)

        # Wizard header with Tutorial button
        wizard_header_layout = QHBoxLayout()
        wizard_title = QLabel("Create Your Lesson")
        wizard_title.setFont(QFont('', 14, QFont.Weight.Bold))
        wizard_title.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; background: transparent;")
        wizard_header_layout.addWidget(wizard_title)
        wizard_header_layout.addStretch()

        tutorial_btn = QPushButton("Tutorial")
        tutorial_btn.setMinimumHeight(36)
        tutorial_btn.clicked.connect(self.show_tutorial)
        tutorial_btn.setAccessibleName("Open tutorial guide")
        tutorial_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SUCCESS};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1ea54e;
            }}
            QPushButton:focus {{
                outline: 2px solid {COLOR_SUCCESS};
                outline-offset: 2px;
            }}
        """)
        wizard_header_layout.addWidget(tutorial_btn)
        wizard_layout.addLayout(wizard_header_layout)

        # Progress indicator
        self.progress_layout = QHBoxLayout()
        self.step_labels = []
        step_names = ["Objective", "Needs", "UDL", "Resources", "Interests", "Refine", "Generate"]
        for i, name in enumerate(step_names):
            label = QPushButton(f"{i+1}. {name}")
            label.setFlat(True)
            label.setEnabled(False)
            label.clicked.connect(partial(self.go_to_step, i))
            self.step_labels.append(label)
            self.progress_layout.addWidget(label)
        wizard_layout.addLayout(self.progress_layout)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        wizard_layout.addWidget(line)

        # Stacked widget for steps
        self.stack = QStackedWidget()

        # Create step widgets
        self.steps = [
            StepObjective(self.form_data),
            StepNeeds(self.form_data),
            StepUDL(self.form_data),
            StepResources(self.form_data),
            StepInterests(self.form_data),
            StepConversation(self.form_data, self.ollama),
            StepGenerate(self.form_data, self.ollama, self.storage)
        ]

        # Connect save_to_dashboard signal from StepGenerate
        self.steps[-1].save_to_dashboard_requested = self.save_assignment_to_dashboard

        for step in self.steps:
            scroll = QScrollArea()
            scroll.setWidget(step)
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            self.stack.addWidget(scroll)

        wizard_layout.addWidget(self.stack, 1)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self.prev_step)
        nav_layout.addWidget(self.prev_btn)

        nav_layout.addStretch()

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.next_step)
        nav_layout.addWidget(self.next_btn)

        wizard_layout.addLayout(nav_layout)

        self.main_view_stack.addWidget(wizard_widget)

        # === Dashboard View (index 1) ===
        self.dashboard = DashboardWidget(self.storage)
        self.dashboard.load_assignment_requested.connect(self.load_assignment_from_dashboard)
        self.dashboard.back_to_wizard_requested.connect(self.show_wizard_view)
        self.main_view_stack.addWidget(self.dashboard)

        app_layout.addWidget(self.main_view_stack, 1)

        self.app_stack.addWidget(self.main_app_widget)
        main_layout.addWidget(self.app_stack)

        # Update initial state
        self.update_navigation()

    def _style_nav_button(self, button, active=False):
        """Apply navigation button styling with active state support."""
        if active:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_PRIMARY};
                    color: white;
                    border: 1px solid {COLOR_PRIMARY};
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_PRIMARY_DARK};
                    border: 1px solid {COLOR_PRIMARY_DARK};
                }}
                QPushButton:focus {{
                    outline: 2px solid {COLOR_PRIMARY_LIGHT};
                    outline-offset: 2px;
                }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_BACKGROUND_ALT};
                    color: {COLOR_TEXT_PRIMARY};
                    border: 1px solid {COLOR_BORDER};
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_SURFACE};
                    border: 1px solid {COLOR_PRIMARY};
                }}
                QPushButton:pressed {{
                    background-color: {COLOR_PRIMARY};
                    color: white;
                    border: 1px solid {COLOR_PRIMARY};
                }}
                QPushButton:focus {{
                    outline: 2px solid {COLOR_PRIMARY_LIGHT};
                    outline-offset: 2px;
                }}
            """)

    def _set_active_nav_button(self, button):
        """Set the active navigation button (stays highlighted until another is clicked)."""
        self.active_nav_button = button
        for btn in self.nav_buttons:
            self._style_nav_button(btn, active=(btn == button))

    def _on_nav_button_clicked(self, button, action):
        """Handle navigation button click - set active state and run action."""
        self._set_active_nav_button(button)
        action()

    def _style_secondary_button(self, button):
        """Apply secondary button styling (dark theme)."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BACKGROUND_ALT};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_SURFACE};
                border: 1px solid {COLOR_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: 1px solid {COLOR_PRIMARY};
            }}
            QPushButton:focus {{
                outline: 2px solid {COLOR_PRIMARY_LIGHT};
                outline-offset: 2px;
            }}
        """)

    def update_navigation(self):
        """Update navigation buttons and step indicators."""
        self.prev_btn.setEnabled(self.current_step > 0)
        self.next_btn.setEnabled(self.current_step < len(self.steps) - 1)

        if self.current_step == len(self.steps) - 1:
            self.next_btn.setText("Finish")
        else:
            self.next_btn.setText("Next →")

        # Update step labels with brand colors (dark theme)
        for i, label in enumerate(self.step_labels):
            label.setEnabled(True)
            if i < self.current_step:
                label.setStyleSheet(f"color: {COLOR_SUCCESS}; font-weight: bold; background: transparent;")
            elif i == self.current_step:
                label.setStyleSheet(f"color: {COLOR_PRIMARY}; font-weight: bold; background: transparent;")
            else:
                label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; background: transparent;")

    def go_to_step(self, step: int):
        """Navigate to a specific step."""
        if 0 <= step < len(self.steps):
            # Validate current step before moving forward
            if step > self.current_step:
                valid, message = self.steps[self.current_step].validate()
                if not valid:
                    QMessageBox.warning(self, "Validation Error", message)
                    return

            self.current_step = step
            self.stack.setCurrentIndex(step)
            self.steps[step].load_data()
            self.update_navigation()

    def next_step(self):
        """Go to next step."""
        valid, message = self.steps[self.current_step].validate()
        if not valid:
            QMessageBox.warning(self, "Validation Error", message)
            return

        if self.current_step < len(self.steps) - 1:
            self.go_to_step(self.current_step + 1)

    def prev_step(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.go_to_step(self.current_step - 1)

    def show_tutorial(self):
        """Show the wizard tutorial dialog."""
        dialog = TutorialDialog(self)
        dialog.exec()

    def open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self.storage, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Reload Ollama settings
            prefs = self.storage.get_preferences()
            self.ollama = OllamaService(
                endpoint=prefs.get('ollama_endpoint', 'http://localhost:11434'),
                model=prefs.get('ollama_model', 'llama3.2')
            )
            # Update conversation and generate steps with new ollama instance
            self.steps[5].ollama = self.ollama
            self.steps[6].ollama = self.ollama

    def toggle_dashboard(self):
        """Toggle between wizard and dashboard views."""
        # Switch to dashboard
        self.dashboard.refresh_list()
        self.dashboard.show_list_view()
        self.main_view_stack.setCurrentIndex(1)
        self._set_active_nav_button(self.dashboard_btn)

    def show_wizard_view(self):
        """Switch to wizard view."""
        self.main_view_stack.setCurrentIndex(0)
        self._set_active_nav_button(self.wizard_btn)

    def save_assignment_to_dashboard(self, name: str, materials: dict):
        """Save the current assignment to the dashboard."""
        self.storage.save_assignment(name, self.form_data.copy(), materials)
        QMessageBox.information(
            self, "Saved",
            f"Assignment '{name}' has been saved to the Dashboard!"
        )

    def load_assignment_from_dashboard(self, assignment: dict):
        """Load an assignment from the dashboard into the wizard."""
        form_data = assignment.get('form_data', {})

        # Update form_data
        self.form_data.update(form_data)

        # Update all steps with new form_data
        for step in self.steps:
            step.form_data = self.form_data
            step.load_data()

        # Switch to wizard view and go to step 1
        self.show_wizard_view()
        self.go_to_step(0)

    def reset_wizard(self):
        """Reset the wizard to initial state."""
        reply = QMessageBox.question(
            self, "Reset Wizard",
            "Are you sure you want to reset? All entered data will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.form_data = get_default_form_data()
            for step in self.steps:
                step.form_data = self.form_data
                step.load_data()
            self.storage.clear_form_autosave()
            self.go_to_step(0)

    def load_autosaved_data(self):
        """Load autosaved form data if available."""
        saved = self.storage.get_autosaved_form()
        if saved:
            reply = QMessageBox.question(
                self, "Restore Previous Session",
                "Found autosaved data from a previous session. Would you like to restore it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.form_data.update(saved)
                for step in self.steps:
                    step.form_data = self.form_data

        # Also apply default grade level if set
        prefs = self.storage.get_preferences()
        default_grade = prefs.get('default_grade_level', '')
        if default_grade and not self.form_data.get('grade_level'):
            self.form_data['grade_level'] = default_grade

        self.steps[0].load_data()

    def setup_autosave(self):
        """Setup autosave timer."""
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(5000)  # Every 5 seconds

    def autosave(self):
        """Autosave current form data."""
        if any(self.form_data.values()):
            self.storage.save_form_autosave(self.form_data)

    def check_existing_session(self):
        """Check if there's an existing login session."""
        username = self.auth.get_current_user()
        if username:
            self.on_authenticated(username)
        else:
            self.app_stack.setCurrentIndex(0)  # Show login

    def on_authenticated(self, username: str):
        """Handle successful authentication."""
        self.current_user = username
        self.user_label.setText(f"Welcome, {username}")
        self.app_stack.setCurrentIndex(1)  # Show main app
        self.load_autosaved_data()
        self.setup_autosave()

    def logout(self):
        """Log out the current user."""
        reply = QMessageBox.question(
            self, "Logout",
            "Are you sure you want to log out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.autosave()
            self.auth.logout()
            self.current_user = None
            self.user_label.setText("")
            self.auth_widget.show_login()
            self.app_stack.setCurrentIndex(0)

    def closeEvent(self, event):
        """Handle window close."""
        if self.current_user:
            self.autosave()
        event.accept()


# ============================================================================
# Entry Point
# ============================================================================

def main():
    # Set environment variable to help with Qt on macOS
    if sys.platform == 'darwin':
        os.environ['QT_MAC_WANTS_LAYER'] = '1'

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set application-wide font
    font = QFont()
    font.setPointSize(11)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
