"""
Ollama AI Service for UDL Differentiation Wizard
Handles all AI interactions with locally running Ollama
"""

import requests
import json
from typing import Callable, Optional


class OllamaService:
    """Service for interacting with Ollama API"""

    def __init__(self, endpoint: str = "http://localhost:11434", model: str = "llama3.2"):
        self.endpoint = endpoint.rstrip('/')
        self.model = model

    def test_connection(self) -> tuple[bool, str, list[str]]:
        """
        Test connection to Ollama and get available models.
        Returns: (success, message, models_list)
        """
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]
                if models:
                    return True, f"Connected! Found {len(models)} model(s)", models
                else:
                    return True, "Connected but no models installed. Run: ollama pull llama3.2", []
            else:
                return False, f"Connection failed: HTTP {response.status_code}", []
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to Ollama. Make sure it's running (ollama serve)", []
        except Exception as e:
            return False, f"Error: {str(e)}", []

    def generate(self, prompt: str, system_prompt: str = "",
                 on_progress: Optional[Callable[[str], None]] = None) -> str:
        """
        Generate a response from Ollama.

        Args:
            prompt: The user prompt
            system_prompt: Optional system context
            on_progress: Optional callback for streaming progress

        Returns:
            Generated text response
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 4096
                }
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = requests.post(
                f"{self.endpoint}/api/generate",
                json=payload,
                stream=True,
                timeout=300
            )

            if response.status_code != 200:
                raise Exception(f"Ollama API error: HTTP {response.status_code}")

            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        chunk = data.get('response', '')
                        full_response += chunk
                        if on_progress and chunk:
                            on_progress(chunk)
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue

            return full_response.strip()

        except requests.exceptions.Timeout:
            raise Exception("Request timed out. The model may be loading or the prompt too long.")
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama. Make sure it's running.")
        except Exception as e:
            raise Exception(f"Generation failed: {str(e)}")

    def chat(self, messages: list[dict], system_prompt: str = "",
             on_progress: Optional[Callable[[str], None]] = None) -> str:
        """
        Chat with Ollama using message history.

        Args:
            messages: List of {"role": "user"|"assistant", "content": str}
            system_prompt: Optional system context
            on_progress: Optional callback for streaming

        Returns:
            Assistant response
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2048
                }
            }

            if system_prompt:
                payload["messages"] = [{"role": "system", "content": system_prompt}] + messages

            response = requests.post(
                f"{self.endpoint}/api/chat",
                json=payload,
                stream=True,
                timeout=300
            )

            if response.status_code != 200:
                raise Exception(f"Ollama API error: HTTP {response.status_code}")

            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        chunk = data.get('message', {}).get('content', '')
                        full_response += chunk
                        if on_progress and chunk:
                            on_progress(chunk)
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue

            return full_response.strip()

        except Exception as e:
            raise Exception(f"Chat failed: {str(e)}")


def build_system_prompt(form_data: dict, version_type: str) -> str:
    """Build the system prompt for generating differentiated materials."""

    version_instructions = {
        'simplified': """
You are creating a SIMPLIFIED version (Below Grade Level) of learning materials.
- Use basic vocabulary appropriate for students 1-2 grade levels below
- Provide more scaffolding and support
- Break concepts into smaller, manageable chunks
- Use concrete examples and visual cues
- Include sentence starters and word banks
- Reduce cognitive load while maintaining learning objectives
""",
        'on_level': """
You are creating an ON-LEVEL version (Grade-Appropriate) of learning materials.
- Use grade-appropriate vocabulary
- Provide balanced support and challenge
- Include clear explanations with examples
- Maintain standard expectations for the grade level
- Include opportunities for practice and application
""",
        'enriched': """
You are creating an ENRICHED version (Above Grade Level) of learning materials.
- Use advanced vocabulary and complex sentence structures
- Encourage deeper analysis and critical thinking
- Include extension activities and challenges
- Provide opportunities for independent exploration
- Connect to broader concepts and real-world applications
- Reduce scaffolding to encourage independent thinking
""",
        'visual_heavy': """
You are creating a VISUAL-HEAVY version of learning materials.
- Minimize text and maximize visual explanations
- Describe images, diagrams, and graphic organizers that should be included
- Use bullet points and numbered lists extensively
- Include visual cues and icons for key concepts
- Suggest charts, infographics, and visual representations
- Format for easy scanning and visual processing
""",
        'scaffolded': """
You are creating a STEP-BY-STEP SCAFFOLDED version of learning materials.
- Break down every task into explicit, numbered steps
- Provide checkpoints and progress markers
- Include explicit instructions for each action
- Add "I do, We do, You do" structure where appropriate
- Include self-monitoring checklists
- Provide clear success criteria for each step
"""
    }

    udl_context = ""
    if form_data.get('engagement'):
        udl_context += f"\nEngagement Strategies: {form_data['engagement']}"
    if form_data.get('representation'):
        udl_context += f"\nRepresentation Methods: {form_data['representation']}"
    if form_data.get('expression'):
        udl_context += f"\nExpression Options: {form_data['expression']}"

    resources_context = ""
    if form_data.get('platforms'):
        resources_context += f"\nAvailable Platforms: {form_data['platforms']}"
    if form_data.get('resources'):
        resources_context += f"\nAvailable Resources: {form_data['resources']}"

    interests_context = ""
    if form_data.get('interests'):
        interests_context += f"\nStudent Interests: {form_data['interests']}"
    if form_data.get('interests_evidence'):
        interests_context += f"\nHow interests were gathered: {form_data['interests_evidence']}"

    return f"""You are an expert educational content creator specializing in Universal Design for Learning (UDL) principles and differentiated instruction.

{version_instructions.get(version_type, version_instructions['on_level'])}

LEARNING CONTEXT:
- Learning Objective: {form_data.get('learning_objective', 'Not specified')}
- Grade Level: {form_data.get('grade_level', 'Not specified')}
- Subject: {form_data.get('subject', 'Not specified')}
- Student Needs: {form_data.get('student_needs', 'Not specified')}
{udl_context}
{resources_context}
{interests_context}

OUTPUT FORMAT:
Create comprehensive learning materials with the following sections:
1. **Introduction** - Hook and learning objective in student-friendly language
2. **Key Concepts** - Main ideas and vocabulary
3. **Instruction** - Teaching content and explanations
4. **Activities** - Practice opportunities and exercises
5. **Assessment** - How students can demonstrate understanding
6. **Accommodations** - Specific supports for this version

Make the content engaging, relevant, and aligned with the learning objective.
Incorporate student interests where natural and appropriate.
Ensure accessibility and WCAG 2.1 AA compliance considerations."""


def build_conversation_prompt(form_data: dict) -> str:
    """Build the system prompt for AI conversation/refinement."""

    return f"""You are an experienced instructional design consultant helping a teacher create differentiated learning materials using Universal Design for Learning (UDL) principles.

Current information provided:
- Learning Objective: {form_data.get('learning_objective', 'Not yet provided')}
- Grade Level: {form_data.get('grade_level', 'Not yet provided')}
- Subject: {form_data.get('subject', 'Not yet provided')}
- Student Needs: {form_data.get('student_needs', 'Not yet provided')}
- UDL Engagement: {form_data.get('engagement', 'Not yet provided')}
- UDL Representation: {form_data.get('representation', 'Not yet provided')}
- UDL Expression: {form_data.get('expression', 'Not yet provided')}
- Platforms: {form_data.get('platforms', 'Not yet provided')}
- Resources: {form_data.get('resources', 'Not yet provided')}
- Student Interests: {form_data.get('interests', 'Not yet provided')}

Your role:
1. Ask clarifying questions to better understand their needs
2. Offer suggestions to improve the learning materials
3. Help them think about differentiation strategies
4. Provide UDL-aligned recommendations
5. Be supportive and collaborative

Keep responses concise and focused. Ask one or two questions at a time."""
