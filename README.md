# UDL Differentiation Wizard - Python Desktop Application

A local desktop application that helps teachers create differentiated learning materials using Universal Design for Learning (UDL) principles and AI-powered content generation via Ollama.

**No coding experience required!** Follow the step-by-step instructions below to get started.

---

## Table of Contents

- [Quick Start Guide](#quick-start-guide)
- [Download Options](#download-options)
- [Step-by-Step Setup](#step-by-step-setup)
- [Features](#features)
- [Dashboard](#dashboard)
- [Using the App](#using-the-app)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Changelog](#changelog)
- [Getting Help](#getting-help)

---

## Quick Start Guide

**What you need:**
1. A Mac or Windows computer
2. About 15 minutes for initial setup
3. Internet connection (for initial download only - the app works offline after setup!)

**Overview of steps:**
1. Download the app files from GitHub
2. Install Python (if you don't have it)
3. Install Ollama (the AI engine)
4. Run the app!

---

## Download Options

### Option 1: Download as ZIP (Easiest - No Git Required)

This is the simplest way to get the app if you're not familiar with Git.

1. **Go to the GitHub page**: https://github.com/Tech-Inclusion-Pro/udl-wizard-python-on-computer

2. **Click the green "Code" button** (near the top right of the page)

3. **Click "Download ZIP"** from the dropdown menu

4. **Find the downloaded file** in your Downloads folder (it will be named something like `udl-wizard-python-on-computer-main.zip`)

5. **Double-click the ZIP file** to extract it (this creates a folder with all the app files)

6. **Move the folder** to a location you'll remember (like your Documents folder)

### Option 2: Clone with Git (For Those Familiar with Git)

If you have Git installed and prefer using the command line:

```bash
git clone https://github.com/Tech-Inclusion-Pro/udl-wizard-python-on-computer.git
cd udl-wizard-python-on-computer
```

---

## Step-by-Step Setup

### Step 1: Install Python

Python is a programming language that runs the app. You need version 3.10 or newer.

**Check if you already have Python:**
1. Open **Terminal** (Mac) or **Command Prompt** (Windows)
   - Mac: Press `Cmd + Space`, type "Terminal", press Enter
   - Windows: Press `Windows key`, type "cmd", press Enter
2. Type `python3 --version` and press Enter
3. If you see a version number like `Python 3.10.x` or higher, you're good! Skip to Step 2.

**If you need to install Python:**

**Mac:**
1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button
3. Open the downloaded file and follow the installer instructions
4. Restart Terminal after installation

**Windows:**
1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button
3. **IMPORTANT:** When installing, check the box that says **"Add Python to PATH"**
4. Click "Install Now"
5. Restart Command Prompt after installation

### Step 2: Install Ollama (The AI Engine)

Ollama runs the AI that generates your differentiated materials. It runs entirely on your computer - no internet needed after setup!

1. **Go to**: https://ollama.ai

2. **Click "Download"** and choose your operating system (Mac or Windows)

3. **Install Ollama:**
   - Mac: Open the downloaded file and drag Ollama to your Applications folder
   - Windows: Run the installer and follow the prompts

4. **Download an AI model** (this is what actually generates the content):
   - Open Terminal (Mac) or Command Prompt (Windows)
   - Type this command and press Enter:
     ```
     ollama pull llama3.2
     ```
   - Wait for the download to complete (this may take a few minutes depending on your internet speed)

5. **Start Ollama:**
   - Mac: Ollama should start automatically. Look for the llama icon in your menu bar.
   - Windows: Ollama should start automatically after installation.

   If it's not running, open Terminal/Command Prompt and type:
   ```
   ollama serve
   ```

### Step 3: Run the App

**Mac:**
1. Open **Terminal** (Press `Cmd + Space`, type "Terminal", press Enter)

2. Navigate to the app folder. Type this command (replace the path with where you saved the folder):
   ```
   cd ~/Documents/udl-wizard-python-on-computer-main
   ```

   **Tip:** You can also type `cd ` (with a space) and then drag the folder into Terminal to auto-fill the path!

3. Run the app:
   ```
   ./run.sh
   ```

   The first time you run this, it will automatically:
   - Create a virtual environment (keeps the app's files organized)
   - Install all required components
   - Launch the app

   This may take a minute or two the first time.

**Windows:**
1. Open **Command Prompt** (Press Windows key, type "cmd", press Enter)

2. Navigate to the app folder:
   ```
   cd C:\Users\YourName\Documents\udl-wizard-python-on-computer-main
   ```
   (Replace `YourName` with your actual username and adjust the path if needed)

3. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install requirements:
   ```
   pip install -r requirements.txt
   ```

5. Run the app:
   ```
   python main.py
   ```

### Step 4: You're Ready!

The app window should now open. You can start creating differentiated materials!

**For future use:**
- Make sure Ollama is running (check for the llama icon)
- Open Terminal/Command Prompt
- Navigate to the app folder
- Run `./run.sh` (Mac) or `python main.py` (Windows)

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
- **100% Offline**: Works entirely on your computer with no internet required (after initial setup)

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

## Using the App

### Before Each Use

Make sure Ollama is running:
- Look for the llama icon in your menu bar (Mac) or system tray (Windows)
- If it's not there, open Terminal/Command Prompt and type: `ollama serve`

### The 7-Step Wizard

1. **Step 1 - Learning Objective**: Define what students should learn and select the grade level
2. **Step 2 - Student Needs**: Describe your students' learning needs and challenges
3. **Step 3 - UDL Principles** (optional): Add details about engagement, representation, and expression
4. **Step 4 - Resources** (optional): List available platforms and teaching resources
5. **Step 5 - Student Interests** (optional): Share what your students are interested in
6. **Step 6 - AI Conversation** (optional): Chat with the AI to refine your inputs
7. **Step 7 - Generate**: Create all 5 versions and export them!

### Exporting Your Materials

After generation, you can export each version as:
- **DOCX** - Microsoft Word document
- **PDF** - Portable document format
- **PPTX** - PowerPoint presentation
- **Excel** - Export all versions to one spreadsheet

### Saving to Dashboard

After generating materials, click **"Save to Dashboard"** to save your work for future reference and reflection.

---

## Configuration

Click **Settings** in the top-right corner to configure:

- **Ollama Endpoint**: Default is `http://localhost:11434` (usually don't need to change this)
- **Model**: Choose from available models
- **Default Save Location**: Where exported files will be saved
- **Default Grade Level**: Pre-fill grade level for new sessions

### Recommended AI Models

Different models have different strengths:
- `llama3.2` (default) - Good balance of speed and quality
- `llama3.1:8b` - Faster, good for quick generations
- `mistral` - Good for educational content
- `mixtral` - Highest quality, but slower

To install a different model, open Terminal/Command Prompt and type:
```
ollama pull modelname
```
(Replace `modelname` with the model you want)

---

## Troubleshooting

### "Cannot connect to Ollama"
- Make sure Ollama is running (look for the llama icon)
- Try opening Terminal/Command Prompt and typing: `ollama serve`
- Check Settings to make sure the endpoint is `http://localhost:11434`

### "No models installed"
- Open Terminal/Command Prompt
- Type: `ollama pull llama3.2`
- Wait for the download to complete

### The app won't start
- Make sure you're in the correct folder in Terminal/Command Prompt
- Try running `./run.sh` (Mac) or `python main.py` (Windows) again
- Check that Python is installed: `python3 --version`

### Generation is very slow
- The first generation after starting is always slower (the AI model needs to load)
- Try a smaller model like `llama3.1:8b`
- Close other programs to free up memory

### Export errors
- Make sure you have permission to save to the selected folder
- Try saving to your Desktop or Documents folder instead

### Grade level dropdown not working (Mac)
- Make sure you're running the latest version
- Restart the app

### I'm getting an error I don't understand
- Take a screenshot of the error
- Check the [Getting Help](#getting-help) section below

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

## Getting Help

### Report Issues
If you encounter a bug or have a problem:
1. Go to: https://github.com/Tech-Inclusion-Pro/udl-wizard-python-on-computer/issues
2. Click "New Issue"
3. Describe the problem and include any error messages

### Request Features
Have an idea to make the app better?
1. Go to: https://github.com/Tech-Inclusion-Pro/udl-wizard-python-on-computer/issues
2. Click "New Issue"
3. Describe the feature you'd like to see

### File Locations

The app stores your data in a hidden folder:
- **Mac/Linux**: `~/.udl-wizard/`
- **Windows**: `C:\Users\YourName\.udl-wizard\`

Files stored:
- `preferences.json` - Your app settings
- `form_autosave.json` - Auto-saved form data
- `assignments.json` - Your saved dashboard assignments

---

## License

This is a clone of the UDL Differentiation Wizard, converted to a Python desktop application for offline use with Ollama.

---

**Made with love for educators everywhere.**
