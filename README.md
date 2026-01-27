# UDL Differentiation Wizard - Python Desktop Application

A local desktop application that helps teachers create differentiated learning materials using Universal Design for Learning (UDL) principles and AI-powered content generation via Ollama.

**No coding experience required!** Follow the step-by-step instructions below to get started.

**Works on:** macOS, Windows, and Linux

---

## Table of Contents

- [Quick Start Guide](#quick-start-guide)
- [Download Options](#download-options)
- [Step-by-Step Setup](#step-by-step-setup)
  - [Step 1: Install Python](#step-1-install-python)
  - [Step 2: Install Ollama](#step-2-install-ollama-the-ai-engine)
  - [Step 3: Run the App](#step-3-run-the-app)
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
1. A Mac, Windows, or Linux computer
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

5. **Extract the ZIP file:**
   - **Mac**: Double-click the ZIP file
   - **Windows**: Right-click → "Extract All..." → Click "Extract"
   - **Linux**: Right-click → "Extract Here" or run `unzip filename.zip` in terminal

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

#### Check if you already have Python

First, open a terminal/command prompt:

| Operating System | How to Open Terminal |
|------------------|---------------------|
| **Mac** | Press `Cmd + Space`, type "Terminal", press Enter |
| **Windows** | Press `Windows key`, type "cmd", press Enter |
| **Linux** | Press `Ctrl + Alt + T` or search for "Terminal" in your applications |

Then type this command and press Enter:
```bash
python3 --version
```

If you see a version number like `Python 3.10.x` or higher, you're good! Skip to [Step 2](#step-2-install-ollama-the-ai-engine).

#### Installing Python

<details>
<summary><strong>Mac Instructions</strong> (click to expand)</summary>

1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button
3. Open the downloaded file and follow the installer instructions
4. Restart Terminal after installation
5. Verify by typing `python3 --version`

</details>

<details>
<summary><strong>Windows Instructions</strong> (click to expand)</summary>

1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button
3. Run the installer
4. **IMPORTANT:** Check the box that says **"Add Python to PATH"** at the bottom of the installer!
5. Click "Install Now"
6. Restart Command Prompt after installation
7. Verify by typing `python --version` or `python3 --version`

</details>

<details>
<summary><strong>Linux Instructions</strong> (click to expand)</summary>

Most Linux distributions come with Python pre-installed. If not, use your package manager:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip
```

Verify installation:
```bash
python3 --version
```

</details>

---

### Step 2: Install Ollama (The AI Engine)

Ollama runs the AI that generates your differentiated materials. It runs entirely on your computer - no internet needed after setup!

#### Installing Ollama

<details>
<summary><strong>Mac Instructions</strong> (click to expand)</summary>

1. Go to https://ollama.ai
2. Click "Download" and select macOS
3. Open the downloaded file
4. Drag Ollama to your Applications folder
5. Open Ollama from Applications (a llama icon will appear in your menu bar)

</details>

<details>
<summary><strong>Windows Instructions</strong> (click to expand)</summary>

1. Go to https://ollama.ai
2. Click "Download" and select Windows
3. Run the installer and follow the prompts
4. Ollama will start automatically (look for the llama icon in your system tray)

</details>

<details>
<summary><strong>Linux Instructions</strong> (click to expand)</summary>

The easiest way to install Ollama on Linux is with the install script:

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

Or if you prefer manual installation, visit https://ollama.ai/download/linux

After installation, start Ollama:
```bash
ollama serve
```

**Tip:** To run Ollama in the background:
```bash
ollama serve &
```

Or set it up as a systemd service for automatic startup:
```bash
sudo systemctl enable ollama
sudo systemctl start ollama
```

</details>

#### Download an AI Model

After installing Ollama, you need to download an AI model. Open your terminal and run:

```bash
ollama pull llama3.2
```

Wait for the download to complete (this may take a few minutes depending on your internet speed - the model is about 2GB).

#### Verify Ollama is Running

- **Mac**: Look for the llama icon in your menu bar (top right of screen)
- **Windows**: Look for the llama icon in your system tray (bottom right of screen)
- **Linux**: Run `ollama list` - if it shows the model, Ollama is running

If Ollama isn't running, open a terminal and type:
```bash
ollama serve
```

---

### Step 3: Run the App

#### Mac & Linux

1. **Open Terminal**
   - Mac: Press `Cmd + Space`, type "Terminal", press Enter
   - Linux: Press `Ctrl + Alt + T` or search for "Terminal"

2. **Navigate to the app folder**

   Type `cd ` (with a space after it), then:
   - **Option A**: Type the full path, for example:
     ```bash
     cd ~/Documents/udl-wizard-python-on-computer-main
     ```
   - **Option B** (Mac): Drag the folder from Finder into the Terminal window to auto-fill the path!
   - **Option B** (Linux): Drag the folder from your file manager into the Terminal

3. **Make the run script executable** (first time only):
   ```bash
   chmod +x run.sh
   ```

4. **Run the app**:
   ```bash
   ./run.sh
   ```

   The first time you run this, it will automatically:
   - Create a virtual environment (keeps the app's files organized)
   - Install all required components
   - Launch the app

   This may take a minute or two the first time.

#### Windows

1. **Open Command Prompt**
   - Press `Windows key`, type "cmd", press Enter

2. **Navigate to the app folder**:
   ```cmd
   cd C:\Users\YourName\Documents\udl-wizard-python-on-computer-main
   ```
   (Replace `YourName` with your actual Windows username)

   **Tip:** You can also type `cd ` and then drag the folder from File Explorer into the Command Prompt window!

3. **Create a virtual environment** (first time only):
   ```cmd
   python -m venv venv
   ```

4. **Activate the virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```
   You should see `(venv)` appear at the beginning of your command line.

5. **Install requirements** (first time only):
   ```cmd
   pip install -r requirements.txt
   ```

6. **Run the app**:
   ```cmd
   python main.py
   ```

#### You're Ready!

The app window should now open. You can start creating differentiated materials!

---

### Running the App in the Future

Once you've completed the initial setup, here's how to run the app next time:

| Step | Mac/Linux | Windows |
|------|-----------|---------|
| 1. Make sure Ollama is running | Check for llama icon or run `ollama serve` | Check for llama icon or run `ollama serve` |
| 2. Open terminal | Terminal app | Command Prompt |
| 3. Go to app folder | `cd ~/Documents/udl-wizard-python-on-computer-main` | `cd C:\Users\YourName\Documents\udl-wizard-python-on-computer-main` |
| 4. Activate environment | (automatic with run.sh) | `venv\Scripts\activate` |
| 5. Run the app | `./run.sh` | `python main.py` |

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
- **Cross-Platform**: Works on Mac, Windows, and Linux

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
- **Mac**: Look for the llama icon in your menu bar
- **Windows**: Look for the llama icon in your system tray
- **Linux**: Run `pgrep ollama` to check, or start with `ollama serve`

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
- **DOCX** - Microsoft Word document (also works with Google Docs, LibreOffice)
- **PDF** - Portable document format (works everywhere)
- **PPTX** - PowerPoint presentation (also works with Google Slides, LibreOffice Impress)
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

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `llama3.2` | Medium | Good | General use (default) |
| `llama3.1:8b` | Fast | Good | Quick generations |
| `mistral` | Medium | Good | Educational content |
| `mixtral` | Slow | Excellent | Highest quality output |

To install a different model, open your terminal and type:
```bash
ollama pull modelname
```
(Replace `modelname` with the model you want, e.g., `ollama pull mistral`)

---

## Troubleshooting

### "Cannot connect to Ollama"

**All platforms:**
1. Make sure Ollama is running
2. Open a terminal and type: `ollama serve`
3. Check Settings to make sure the endpoint is `http://localhost:11434`

**Linux-specific:**
- Check if Ollama is running: `pgrep ollama` or `systemctl status ollama`
- Start Ollama: `ollama serve` or `sudo systemctl start ollama`

### "No models installed"

Open a terminal and run:
```bash
ollama pull llama3.2
```
Wait for the download to complete.

### The app won't start

**Mac/Linux:**
- Make sure you're in the correct folder: `pwd` shows your current location
- Make sure the script is executable: `chmod +x run.sh`
- Try running directly: `./run.sh`
- Check Python is installed: `python3 --version`

**Windows:**
- Make sure you activated the virtual environment: `venv\Scripts\activate`
- Look for `(venv)` at the start of your command line
- Try: `python main.py`

**Linux-specific:**
- If you get permission errors, don't use `sudo` - instead fix permissions:
  ```bash
  chmod +x run.sh
  ```
- If you get "python3 not found", install it with your package manager (see [Step 1](#step-1-install-python))

### Generation is very slow

- The first generation after starting is always slower (the AI model needs to load into memory)
- Try a smaller, faster model: `ollama pull llama3.1:8b`
- Close other programs to free up memory
- Check your system has enough RAM (8GB minimum recommended, 16GB ideal)

### Export errors

- Make sure you have permission to save to the selected folder
- Try saving to your Desktop or Documents folder
- **Linux**: Check folder permissions with `ls -la`

### Grade level dropdown not working (Mac)

- Make sure you're running the latest version
- Restart the app

### PyQt6 issues on Linux

If you get errors about Qt or PyQt6:

**Ubuntu/Debian:**
```bash
sudo apt install python3-pyqt6 libxcb-xinerama0
```

**Fedora:**
```bash
sudo dnf install python3-qt6
```

**If you still have issues**, try installing system Qt libraries:
```bash
# Ubuntu/Debian
sudo apt install qt6-base-dev

# Fedora
sudo dnf install qt6-qtbase-devel
```

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
3. Describe the problem and include:
   - Your operating system (Mac, Windows, or Linux distribution)
   - Any error messages you see
   - Steps to reproduce the problem

### Request Features

Have an idea to make the app better?
1. Go to: https://github.com/Tech-Inclusion-Pro/udl-wizard-python-on-computer/issues
2. Click "New Issue"
3. Describe the feature you'd like to see

### File Locations

The app stores your data in a hidden folder in your home directory:

| Operating System | Location |
|------------------|----------|
| **Mac** | `~/.udl-wizard/` |
| **Windows** | `C:\Users\YourName\.udl-wizard\` |
| **Linux** | `~/.udl-wizard/` |

Files stored:
- `preferences.json` - Your app settings
- `form_autosave.json` - Auto-saved form data
- `assignments.json` - Your saved dashboard assignments

To find this folder:
- **Mac**: In Finder, press `Cmd + Shift + G` and type `~/.udl-wizard`
- **Windows**: Type `%USERPROFILE%\.udl-wizard` in File Explorer's address bar
- **Linux**: Run `ls -la ~/.udl-wizard` or enable "Show Hidden Files" in your file manager

---

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | macOS 10.15+, Windows 10+, or Linux (Ubuntu 20.04+, Fedora 35+, etc.) | Latest OS version |
| **Python** | 3.10 | 3.11 or 3.12 |
| **RAM** | 8 GB | 16 GB |
| **Disk Space** | 5 GB (for Ollama + model) | 10 GB |
| **Processor** | Any modern CPU | Apple Silicon (M1/M2) or recent Intel/AMD |

---

## License

This is a clone of the UDL Differentiation Wizard, converted to a Python desktop application for offline use with Ollama.

---

**Made with love for educators everywhere.**

*Works on Mac, Windows, and Linux!*
