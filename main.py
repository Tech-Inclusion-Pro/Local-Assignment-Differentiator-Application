#!/usr/bin/env python3
"""
UDL Differentiation Wizard - Python Desktop Application
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
    QMessageBox, QFileDialog, QDialog, QDialogButtonBox,
    QTabWidget, QSplitter, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor

from ollama_service import OllamaService, build_system_prompt, build_conversation_prompt
from export_service import (
    export_to_docx, export_to_pdf, export_to_pptx, export_all_to_xlsx,
    VERSION_NAMES
)
from storage_service import StorageService, get_default_form_data


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
# Settings Dialog
# ============================================================================

class SettingsDialog(QDialog):
    """Dialog for configuring Ollama and app settings."""

    def __init__(self, storage: StorageService, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
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
        self.test_btn.setEnabled(False)

        endpoint = self.endpoint_input.text() or 'http://localhost:11434'
        ollama = OllamaService(endpoint)
        success, message, models = ollama.test_connection()

        if success and models:
            self.test_status.setText(f"✓ {message}")
            self.test_status.setStyleSheet("color: green;")
            # Update model dropdown with available models
            current = self.model_input.currentText()
            self.model_input.clear()
            self.model_input.addItems(models)
            if current in models:
                self.model_input.setCurrentText(current)
        else:
            self.test_status.setText(f"✗ {message}")
            self.test_status.setStyleSheet("color: red;")

        self.test_btn.setEnabled(True)


# ============================================================================
# Wizard Step Widgets
# ============================================================================

class StepObjective(QWidget):
    """Step 1: Learning Objective"""

    def __init__(self, form_data: dict):
        super().__init__()
        self.form_data = form_data
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
        self.form_data['learning_objective'] = self.objective_input.toPlainText()
        grade = self.grade_combo.currentText()
        self.form_data['grade_level'] = '' if grade == 'Select...' else grade
        self.form_data['subject'] = self.subject_input.text()

    def load_data(self):
        self.objective_input.setPlainText(self.form_data.get('learning_objective', ''))
        grade = self.form_data.get('grade_level', '')
        index = self.grade_combo.findText(grade) if grade else 0
        self.grade_combo.setCurrentIndex(max(0, index))
        self.subject_input.setText(self.form_data.get('subject', ''))

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
        engage_desc.setStyleSheet("color: gray;")
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
        rep_desc.setStyleSheet("color: gray;")
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
        exp_desc.setStyleSheet("color: gray;")
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

        # Export all button
        export_all_layout = QHBoxLayout()
        export_all_layout.addStretch()
        self.export_all_btn = QPushButton("Export All to Excel")
        self.export_all_btn.clicked.connect(self.export_all_xlsx)
        self.export_all_btn.setEnabled(False)
        export_all_layout.addWidget(self.export_all_btn)
        layout.addLayout(export_all_layout)

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

    def load_data(self):
        pass  # Results don't persist

    def validate(self) -> tuple[bool, str]:
        return True, ""


# ============================================================================
# Main Application Window
# ============================================================================

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.storage = StorageService()
        self.form_data = get_default_form_data()

        # Initialize Ollama with saved settings
        prefs = self.storage.get_preferences()
        self.ollama = OllamaService(
            endpoint=prefs.get('ollama_endpoint', 'http://localhost:11434'),
            model=prefs.get('ollama_model', 'llama3.2')
        )

        self.current_step = 0
        self.steps = []

        self.setup_ui()
        self.load_autosaved_data()
        self.setup_autosave()

    def setup_ui(self):
        self.setWindowTitle("UDL Differentiation Wizard")
        self.setMinimumSize(900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("UDL Differentiation Wizard")
        title_label.setFont(QFont('', 20, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_wizard)
        header_layout.addWidget(reset_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(settings_btn)

        main_layout.addLayout(header_layout)

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
        main_layout.addLayout(self.progress_layout)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(line)

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

        for step in self.steps:
            scroll = QScrollArea()
            scroll.setWidget(step)
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            self.stack.addWidget(scroll)

        main_layout.addWidget(self.stack, 1)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self.prev_step)
        nav_layout.addWidget(self.prev_btn)

        nav_layout.addStretch()

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.next_step)
        nav_layout.addWidget(self.next_btn)

        main_layout.addLayout(nav_layout)

        # Update initial state
        self.update_navigation()

    def update_navigation(self):
        """Update navigation buttons and step indicators."""
        self.prev_btn.setEnabled(self.current_step > 0)
        self.next_btn.setEnabled(self.current_step < len(self.steps) - 1)

        if self.current_step == len(self.steps) - 1:
            self.next_btn.setText("Finish")
        else:
            self.next_btn.setText("Next →")

        # Update step labels
        for i, label in enumerate(self.step_labels):
            label.setEnabled(True)
            if i < self.current_step:
                label.setStyleSheet("color: green; font-weight: bold;")
            elif i == self.current_step:
                label.setStyleSheet("color: #6B46C1; font-weight: bold;")
            else:
                label.setStyleSheet("color: gray;")

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

    def closeEvent(self, event):
        """Handle window close."""
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
