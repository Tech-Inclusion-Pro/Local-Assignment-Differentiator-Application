#!/usr/bin/env python3
"""
Build script to create a macOS .app bundle for Assignment Differentiation Application
"""

import subprocess
import sys
import os

def main():
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("=" * 60)
    print("Building Assignment Differentiation Application")
    print("=" * 60)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # PyInstaller command - using minimal options that work
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=Assignment Differentiation Application",
        "--windowed",  # No console window
        "--onedir",    # Create a directory bundle
        "--noconfirm", # Replace existing build
        "--clean",     # Clean cache
        # Application icon
        "--icon=assets/AppIcon.icns",
        # Add the other Python files as data
        "--add-data=ollama_service.py:.",
        "--add-data=export_service.py:.",
        "--add-data=storage_service.py:.",
        "--add-data=auth_service.py:.",
        # Add assets folder
        "--add-data=assets:assets",
        # macOS specific
        "--osx-bundle-identifier=com.assignmentdiff.app",
        "main.py"
    ]

    print("\nRunning PyInstaller...")
    print("-" * 60)

    try:
        subprocess.check_call(cmd)
        print("-" * 60)
        print("\n✓ Build complete!")
        print(f"\nApplication created at:")
        print(f"  {script_dir}/dist/Assignment Differentiation Application.app")
        print(f"\nTo install, run:")
        print(f"  ditto 'dist/Assignment Differentiation Application.app' '/Applications/Assignment Differentiation Application.app'")
        print(f"\nOr drag the .app to your Applications folder.")

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
