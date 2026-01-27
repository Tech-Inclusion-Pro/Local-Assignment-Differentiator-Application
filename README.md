# UDL Differentiation Wizard - Python Desktop Application

A local desktop application that helps teachers create differentiated learning materials using Universal Design for Learning (UDL) principles and AI-powered content generation via Ollama.

## Features

- **7-Step Guided Wizard**: Walk through defining learning objectives, student needs, UDL principles, resources, and student interests
- **AI-Powered Generation**: Creates 5 differentiated versions of your materials:
  - Simplified (Below Grade Level)
  - On-Level (Grade Appropriate)
  - Enriched (Above Grade Level)
  - Visual-Heavy
  - Step-by-Step Scaffolded
- **AI Conversation**: Chat with AI to refine your inputs before generation
- **Multiple Export Formats**: DOCX, PDF, PowerPoint, and Excel
- **Auto-Save**: Your work is automatically saved and can be restored
- **100% Offline**: Works entirely on your computer with no internet required

## Prerequisites

1. **Python 3.10+** installed on your system
2. **Ollama** installed and running locally
   - Install from: https://ollama.ai
   - Pull a model: `ollama pull llama3.2`
   - Start the server: `ollama serve`

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

4. **Export your materials** in your preferred format(s)

## Configuration

Click **Settings** in the top-right corner to configure:

- **Ollama Endpoint**: Default is `http://localhost:11434`
- **Model**: Choose from available models (test connection to see installed models)
- **Default Save Location**: Where exported files will be saved
- **Default Grade Level**: Pre-fill grade level for new sessions

## File Structure

```
udl-wizard-python/
├── main.py              # Main application with PyQt6 GUI
├── ollama_service.py    # Ollama API integration and prompts
├── export_service.py    # Document export (DOCX, PDF, PPTX, XLSX)
├── storage_service.py   # Settings and autosave persistence
├── requirements.txt     # Python dependencies
├── run.sh              # Quick-start script
└── README.md           # This file
```

## Data Storage

The application stores settings and autosaved data in:
- macOS/Linux: `~/.udl-wizard/`
- Contents:
  - `preferences.json` - App settings
  - `form_autosave.json` - Auto-saved form data
  - `templates.json` - Saved templates (future feature)

## Recommended Models

For best results, use one of these Ollama models:
- `llama3.2` (default, good balance)
- `llama3.1:8b` (faster, smaller)
- `mistral` (good for educational content)
- `mixtral` (highest quality, slower)

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

## License

This is a clone of the UDL Differentiation Wizard, converted to a Python desktop application for offline use with Ollama.
