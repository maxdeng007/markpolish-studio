#!/usr/bin/env python3
"""
MarkPolish Studio Launch Script
Double-click this file or run: python3 launch.py
"""

import os
import sys
import subprocess
import platform

def main():
    # Get the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print("🚀 MarkPolish Studio - Launch Script")
    print("=" * 40)
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✓ Python version: {sys.version.split()[0]}")
    print()
    
    # Check if virtual environment exists
    venv_path = os.path.join(project_dir, "venv")
    if not os.path.exists(venv_path):
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created")
    else:
        print("✓ Virtual environment found")
    
    # Determine the Python executable in venv
    if platform.system() == "Windows":
        venv_python = os.path.join(venv_path, "Scripts", "python.exe")
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        venv_python = os.path.join(venv_path, "bin", "python")
        pip_path = os.path.join(venv_path, "bin", "pip")
    
    # Install/update dependencies
    print("📥 Installing/updating dependencies...")
    subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip", "--quiet"], check=True)
    subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"], check=True)
    
    print()
    print("✅ Setup complete!")
    print()
    print("🌐 Starting MarkPolish Studio...")
    print("   The app will open in your browser at http://localhost:8501")
    print()
    print("   Press Ctrl+C to stop the server")
    print()
    
    # Run Streamlit
    streamlit_path = os.path.join(venv_path, "bin" if platform.system() != "Windows" else "Scripts", "streamlit")
    if not os.path.exists(streamlit_path):
        streamlit_path = "streamlit"  # Fallback to system streamlit
    
    subprocess.run([venv_python, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

