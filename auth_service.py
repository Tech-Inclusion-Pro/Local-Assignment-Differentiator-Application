"""
Authentication Service for Assignment Differentiation Application
Handles user registration, login, and password recovery using security questions.
"""

import json
import hashlib
import secrets
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime


# Security questions pool
SECURITY_QUESTIONS = [
    "What was the name of your first pet?",
    "What city were you born in?",
    "What is your mother's maiden name?",
    "What was the name of your elementary school?",
    "What was your childhood nickname?",
    "What is the name of the street you grew up on?",
    "What was the make of your first car?",
    "What is your favorite book?",
    "What was your favorite food as a child?",
    "What is the middle name of your oldest sibling?",
]


class AuthService:
    """Manages user authentication using JSON file storage."""

    def __init__(self):
        self.storage_dir = Path.home() / '.udl-wizard'
        self.storage_dir.mkdir(exist_ok=True)
        self.users_file = self.storage_dir / 'users.json'
        self.session_file = self.storage_dir / 'session.json'

    def _load_users(self) -> dict:
        """Load users from JSON file."""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return {'users': {}}

    def _save_users(self, data: dict) -> bool:
        """Save users to JSON file."""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False

    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash a password with salt using SHA-256."""
        if salt is None:
            salt = secrets.token_hex(16)
        hashed = hashlib.sha256((salt + password).encode()).hexdigest()
        return hashed, salt

    def _hash_answer(self, answer: str) -> str:
        """Hash a security question answer (case-insensitive)."""
        normalized = answer.strip().lower()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def register(
        self,
        username: str,
        password: str,
        security_questions: list[dict]
    ) -> Tuple[bool, str]:
        """
        Register a new user.

        Args:
            username: The username
            password: The password (will be hashed)
            security_questions: List of dicts with 'question' and 'answer' keys (3 required)

        Returns:
            Tuple of (success, message)
        """
        # Validate inputs
        username = username.strip()
        if not username:
            return False, "Username is required."
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        if not password:
            return False, "Password is required."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        if len(security_questions) < 3:
            return False, "Three security questions are required."

        # Check all security questions have answers
        for sq in security_questions:
            if not sq.get('answer', '').strip():
                return False, "All security questions must be answered."

        # Load existing users
        data = self._load_users()

        # Check if username exists (case-insensitive)
        username_lower = username.lower()
        for existing_user in data['users'].keys():
            if existing_user.lower() == username_lower:
                return False, "Username already exists."

        # Hash password
        password_hash, salt = self._hash_password(password)

        # Hash security question answers
        hashed_questions = []
        for sq in security_questions:
            hashed_questions.append({
                'question': sq['question'],
                'answer_hash': self._hash_answer(sq['answer'])
            })

        # Create user record
        data['users'][username] = {
            'password_hash': password_hash,
            'salt': salt,
            'security_questions': hashed_questions,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }

        if self._save_users(data):
            return True, "Registration successful!"
        return False, "Failed to save user data."

    def login(self, username: str, password: str, stay_logged_in: bool = False) -> Tuple[bool, str]:
        """
        Authenticate a user.

        Args:
            username: The username
            password: The password
            stay_logged_in: If True, session persists across app restarts

        Returns:
            Tuple of (success, message)
        """
        username = username.strip()
        if not username or not password:
            return False, "Username and password are required."

        data = self._load_users()

        # Find user (case-insensitive username lookup)
        user = None
        actual_username = None
        for uname, udata in data['users'].items():
            if uname.lower() == username.lower():
                user = udata
                actual_username = uname
                break

        if not user:
            return False, "Invalid username or password."

        # Verify password
        password_hash, _ = self._hash_password(password, user['salt'])
        if password_hash != user['password_hash']:
            return False, "Invalid username or password."

        # Update last login
        user['last_login'] = datetime.now().isoformat()
        self._save_users(data)

        # Save session (with stay_logged_in preference)
        self._save_session(actual_username, stay_logged_in)

        return True, "Login successful!"

    def logout(self) -> bool:
        """Clear the current session."""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            return True
        except IOError:
            return False

    def _save_session(self, username: str, stay_logged_in: bool = False) -> bool:
        """Save session data."""
        try:
            session = {
                'username': username,
                'logged_in_at': datetime.now().isoformat(),
                'stay_logged_in': stay_logged_in
            }
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2)
            return True
        except IOError:
            return False

    def get_current_user(self) -> Optional[str]:
        """Get the currently logged-in user, if any.

        Only returns a user if stay_logged_in was enabled during login.
        """
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    # Only auto-login if stay_logged_in was enabled
                    if session.get('stay_logged_in', False):
                        return session.get('username')
        except (json.JSONDecodeError, IOError):
            pass
        return None

    def get_security_questions(self, username: str) -> Optional[list[str]]:
        """Get the security questions for a user (for password recovery)."""
        data = self._load_users()

        # Find user (case-insensitive)
        for uname, udata in data['users'].items():
            if uname.lower() == username.lower():
                questions = udata.get('security_questions', [])
                return [q['question'] for q in questions]

        return None

    def verify_security_answers(
        self,
        username: str,
        answers: list[str]
    ) -> Tuple[bool, str]:
        """
        Verify security question answers.

        Args:
            username: The username
            answers: List of answers in order of the security questions

        Returns:
            Tuple of (success, message)
        """
        data = self._load_users()

        # Find user (case-insensitive)
        user = None
        for uname, udata in data['users'].items():
            if uname.lower() == username.lower():
                user = udata
                break

        if not user:
            return False, "User not found."

        stored_questions = user.get('security_questions', [])
        if len(answers) != len(stored_questions):
            return False, "Incorrect number of answers."

        # Verify each answer
        for i, sq in enumerate(stored_questions):
            answer_hash = self._hash_answer(answers[i])
            if answer_hash != sq['answer_hash']:
                return False, "One or more answers are incorrect."

        return True, "Security answers verified."

    def reset_password(
        self,
        username: str,
        new_password: str,
        answers: list[str]
    ) -> Tuple[bool, str]:
        """
        Reset a user's password after verifying security questions.

        Args:
            username: The username
            new_password: The new password
            answers: List of security question answers

        Returns:
            Tuple of (success, message)
        """
        # First verify security answers
        verified, message = self.verify_security_answers(username, answers)
        if not verified:
            return False, message

        # Validate new password
        if not new_password:
            return False, "New password is required."
        if len(new_password) < 6:
            return False, "Password must be at least 6 characters."

        data = self._load_users()

        # Find and update user (case-insensitive)
        for uname, udata in data['users'].items():
            if uname.lower() == username.lower():
                password_hash, salt = self._hash_password(new_password)
                udata['password_hash'] = password_hash
                udata['salt'] = salt
                if self._save_users(data):
                    return True, "Password reset successful!"
                return False, "Failed to save new password."

        return False, "User not found."

    def user_exists(self, username: str) -> bool:
        """Check if a username exists."""
        data = self._load_users()
        username_lower = username.lower()
        for uname in data['users'].keys():
            if uname.lower() == username_lower:
                return True
        return False


def get_security_questions_list() -> list[str]:
    """Return the list of available security questions."""
    return SECURITY_QUESTIONS.copy()
