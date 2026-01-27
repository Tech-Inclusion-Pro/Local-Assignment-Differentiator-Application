#!/usr/bin/env python3
"""
Build script to create a macOS .app bundle for UDL Differentiation Wizard
"""

import subprocess
import sys
import os

def main():
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("=" * 60)
    print("Building UDL Differentiation Wizard macOS Application")
    print("=" * 60)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=UDL Differentiation Wizard",
        "--windowed",  # No console window
        "--onedir",    # Create a directory bundle
        "--noconfirm", # Replace existing build
        "--clean",     # Clean cache
        # Hidden imports for PyQt6 and other dependencies
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=docx",
        "--hidden-import=docx.shared",
        "--hidden-import=docx.enum.text",
        "--hidden-import=reportlab",
        "--hidden-import=reportlab.lib",
        "--hidden-import=reportlab.platypus",
        "--hidden-import=pptx",
        "--hidden-import=pptx.util",
        "--hidden-import=openpyxl",
        "--hidden-import=markdown",
        "--hidden-import=requests",
        # Collect all data for packages that need it
        "--collect-all=docx",
        "--collect-all=pptx",
        "--collect-all=reportlab",
        # Add the other Python files as data
        "--add-data=ollama_service.py:.",
        "--add-data=export_service.py:.",
        "--add-data=storage_service.py:.",
        # macOS specific
        "--osx-bundle-identifier=com.udlwizard.app",
        "main.py"
    ]

    print("\nRunning PyInstaller...")
    print("-" * 60)

    try:
        subprocess.check_call(cmd)
        print("-" * 60)
        print("\n✓ Build complete!")
        print(f"\nApplication created at:")
        print(f"  {script_dir}/dist/UDL Differentiation Wizard.app")
        print(f"\nTo install, run:")
        print(f"  cp -r 'dist/UDL Differentiation Wizard.app' /Applications/")
        print(f"\nOr drag the .app to your Applications folder.")

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
