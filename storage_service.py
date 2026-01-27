"""
Storage Service for UDL Differentiation Wizard
Handles persistent storage of preferences and form data using JSON files
"""

import json
import os
from typing import Optional, Any
from pathlib import Path


class StorageService:
    """Manages persistent storage using JSON files in user's home directory."""

    def __init__(self):
        # Store in user's home directory under .udl-wizard
        self.storage_dir = Path.home() / '.udl-wizard'
        self.storage_dir.mkdir(exist_ok=True)

        self.preferences_file = self.storage_dir / 'preferences.json'
        self.form_autosave_file = self.storage_dir / 'form_autosave.json'
        self.templates_file = self.storage_dir / 'templates.json'

    def _load_json(self, filepath: Path) -> dict:
        """Load JSON from file, return empty dict if doesn't exist."""
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return {}

    def _save_json(self, filepath: Path, data: dict) -> bool:
        """Save dict to JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False

    # Preferences
    def get_preferences(self) -> dict:
        """Get all preferences with defaults."""
        defaults = {
            'ollama_endpoint': 'http://localhost:11434',
            'ollama_model': 'llama3.2',
            'default_grade_level': '',
            'default_save_path': str(Path.home() / 'Desktop'),
            'auto_save_enabled': True,
            'theme': 'system'  # 'light', 'dark', 'system'
        }
        stored = self._load_json(self.preferences_file)
        return {**defaults, **stored}

    def save_preferences(self, preferences: dict) -> bool:
        """Save preferences."""
        return self._save_json(self.preferences_file, preferences)

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a single preference value."""
        prefs = self.get_preferences()
        return prefs.get(key, default)

    def set_preference(self, key: str, value: Any) -> bool:
        """Set a single preference value."""
        prefs = self.get_preferences()
        prefs[key] = value
        return self.save_preferences(prefs)

    # Form Auto-save
    def get_autosaved_form(self) -> Optional[dict]:
        """Get autosaved form data if it exists."""
        data = self._load_json(self.form_autosave_file)
        return data if data else None

    def save_form_autosave(self, form_data: dict) -> bool:
        """Auto-save form data."""
        return self._save_json(self.form_autosave_file, form_data)

    def clear_form_autosave(self) -> bool:
        """Clear autosaved form data."""
        try:
            if self.form_autosave_file.exists():
                self.form_autosave_file.unlink()
            return True
        except IOError:
            return False

    # Templates
    def get_templates(self) -> list[dict]:
        """Get saved templates."""
        data = self._load_json(self.templates_file)
        return data.get('templates', [])

    def save_template(self, name: str, form_data: dict) -> bool:
        """Save a form as a named template."""
        templates = self.get_templates()

        # Check if template with same name exists, update it
        for i, t in enumerate(templates):
            if t.get('name') == name:
                templates[i] = {'name': name, 'data': form_data}
                return self._save_json(self.templates_file, {'templates': templates})

        # Add new template
        templates.append({'name': name, 'data': form_data})
        return self._save_json(self.templates_file, {'templates': templates})

    def delete_template(self, name: str) -> bool:
        """Delete a template by name."""
        templates = self.get_templates()
        templates = [t for t in templates if t.get('name') != name]
        return self._save_json(self.templates_file, {'templates': templates})

    def get_template(self, name: str) -> Optional[dict]:
        """Get a specific template by name."""
        templates = self.get_templates()
        for t in templates:
            if t.get('name') == name:
                return t.get('data')
        return None


def get_default_form_data() -> dict:
    """Return empty form data with all fields initialized."""
    return {
        'learning_objective': '',
        'grade_level': '',
        'subject': '',
        'student_needs': '',
        'engagement': '',
        'representation': '',
        'expression': '',
        'platforms': '',
        'resources': '',
        'interests': '',
        'interests_evidence': ''
    }
