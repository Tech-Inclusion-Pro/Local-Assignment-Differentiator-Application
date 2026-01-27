# UDL Differentiation Wizard - Python Desktop Application

A local desktop application that helps teachers create differentiated learning materials using Universal Design for Learning (UDL) principles and AI-powered content generation via Ollama.

---

## Table of Contents

- [Features](#features)
- [Dashboard](#dashboard)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [File Structure](#file-structure)
- [Data Storage](#data-storage)
- [Recommended Models](#recommended-models)
- [Troubleshooting](#troubleshooting)
- [Changelog](#changelog)
- [License](#license)

---

## Features

- **7-Step Guided Wizard**: Walk through defining learning objectives, student needs, UDL principles, resources, and student interests
- **AI-Powered Generation**: Creates 5 differentiated versions of your materials:
  - Simplified (Below Grade Level)
  - On-Level (Grade Appropriate)
  - Enriched (Above Grade Level)
  - Visual-Heavy
  - Step-by-Step Scaffolded
- **Dashboard**: Save, review, and reflect on assignments you've created
- **AI Conversation**: Chat with AI to refine your inputs before generation
- **Multiple Export Formats**: DOCX, PDF, PowerPoint, and Excel
- **Auto-Save**: Your work is automatically saved and can be restored
- **100% Offline**: Works entirely on your computer with no internet required

---

## Dashboard

The Dashboard allows you to save, review, and reflect on assignments you've created. This helps you track what works well and reuse successful lesson materials.

### Accessing the Dashboard

Click the **Dashboard** button in the top header to switch between the Wizard and Dashboard views. The button toggles between "Dashboard" and "Wizard" depending on your current view.

### Saving Assignments

1. Complete the wizard and generate your materials (Step 7)
2. Click **"Save to Dashboard"** button (appears after generation completes)
3. Enter a name for your assignment
4. Your assignment is now saved and accessible from the Dashboard

### Dashboard Features

#### Assignment List View
- View all saved assignments with name, grade level, subject, and creation date
- **Search**: Type in the search box to filter assignments
- **Double-click** an assignment to view its details
- Assignments are sorted by most recently updated

#### Assignment Detail View
When you open an assignment, you can:

- **View the learning objective** and assignment metadata
- **Browse all 5 generated versions** using tabs (Simplified, On-Level, Enriched, Visual, Scaffolded)
- **Export individual versions** to DOCX, PDF, or PPTX format
- **Add reflection notes** with three dedicated fields:
  - *What worked well and why* - Document successful strategies
  - *What did not work well and why* - Note challenges or issues
  - *What could be better next time* - Ideas for improvement
- **Save Reflections** - Persist your notes for future reference

#### Reusing Assignments

Click **"Load into Wizard"** to load a saved assignment back into the wizard. This allows you to:
- Modify the original inputs
- Regenerate materials with adjustments
- Create variations of successful lessons

**Note**: Loading an assignment will replace your current wizard data. You'll be prompted to confirm before proceeding.

---

## Prerequisites

1. **Python 3.10+** installed on your system
2. **Ollama** installed and running locally
   - Install from: https://ollama.ai
   - Pull a model: `ollama pull llama3.2`
   - Start the server: `ollama serve`

---

## Installation

### Option 1: Using the run script (Recommended)

```bash
cd udl-wizard-python
./run.sh
```

The script will automatically:
- Create a virtual environment
- Install all dependencies
- Launch the application

### Option 2: Manual installation

```bash
cd udl-wizard-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 3: macOS App Bundle

If you have a built `.app` bundle, simply double-click it or launch from Launchpad.

To build the app bundle yourself:
```bash
source venv/bin/activate
pip install pyinstaller
pyinstaller "UDL Differentiation Wizard.spec" --noconfirm
# App will be in dist/UDL Differentiation Wizard.app
```

---

## Usage

1. **Start Ollama** before launching the app:
   ```bash
   ollama serve
   ```

2. **Launch the application**:
   ```bash
   ./run.sh
   ```
   or
   ```bash
   source venv/bin/activate && python main.py
   ```

3. **Follow the 7-step wizard**:
   - **Step 1**: Define your learning objective and grade level
   - **Step 2**: Describe your students' learning needs
   - **Step 3**: Apply UDL framework principles (optional)
   - **Step 4**: List available platforms and resources (optional)
   - **Step 5**: Share student interests (optional)
   - **Step 6**: Chat with AI to refine your inputs (optional)
   - **Step 7**: Generate and export your materials

4. **Save to Dashboard** (optional): After generating, click "Save to Dashboard" to store the assignment for future reference

5. **Export your materials** in your preferred format(s)

---

## Configuration

Click **Settings** in the top-right corner to configure:

- **Ollama Endpoint**: Default is `http://localhost:11434`
- **Model**: Choose from available models (test connection to see installed models)
- **Default Save Location**: Where exported files will be saved
- **Default Grade Level**: Pre-fill grade level for new sessions

---

## File Structure

```
udl-wizard-python/
├── main.py              # Main application with PyQt6 GUI
├── ollama_service.py    # Ollama API integration and prompts
├── export_service.py    # Document export (DOCX, PDF, PPTX, XLSX)
├── storage_service.py   # Settings, autosave, and assignments persistence
├── requirements.txt     # Python dependencies
├── run.sh              # Quick-start script
└── README.md           # This file
```

---

## Data Storage

The application stores settings and data in:
- macOS/Linux: `~/.udl-wizard/`
- Contents:
  - `preferences.json` - App settings
  - `form_autosave.json` - Auto-saved form data
  - `templates.json` - Saved templates
  - `assignments.json` - Saved dashboard assignments with reflections

---

## Recommended Models

For best results, use one of these Ollama models:
- `llama3.2` (default, good balance)
- `llama3.1:8b` (faster, smaller)
- `mistral` (good for educational content)
- `mixtral` (highest quality, slower)

---

## Troubleshooting

### "Cannot connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check the endpoint in Settings (default: `http://localhost:11434`)
- Test the connection using the Settings dialog

### "No models installed"
- Pull a model: `ollama pull llama3.2`

### Generation is slow
- Larger models take longer; try a smaller model like `llama3.1:8b`
- First generation may be slow as the model loads into memory

### Export errors
- Make sure you have write permissions to the save location
- Try a different save location

### Grade level dropdown not working
- Make sure you're running the latest version of the app
- If using the macOS app bundle, rebuild it after updates

---

## Changelog

### v1.1.0 (2026-01-26)

**New Features:**
- **Dashboard**: New dashboard view for saving and managing assignments
  - Save completed assignments with custom names
  - View all saved assignments in a searchable list
  - Browse generated content for all 5 differentiated versions
  - Export materials directly from saved assignments
  - Add reflection notes with three fields:
    - "What worked well and why"
    - "What did not work well and why"
    - "What could be better next time"
  - Load saved assignments back into the wizard for reuse or modification
  - Delete assignments you no longer need

**Improvements:**
- Added Dashboard toggle button in the header
- Updated storage service with assignment persistence
- Fixed grade level dropdown compatibility on macOS

### v1.0.0 (2026-01-26)

**Initial Release:**
- 7-step guided wizard for creating differentiated materials
- AI-powered generation of 5 differentiated versions
- AI conversation feature for refining inputs
- Export to DOCX, PDF, PowerPoint, and Excel
- Auto-save and restore functionality
- Settings dialog for Ollama configuration
- macOS app bundle support via PyInstaller

---

## License

This is a clone of the UDL Differentiation Wizard, converted to a Python desktop application for offline use with Ollama.
