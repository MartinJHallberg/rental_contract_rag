#!/usr/bin/env python3
"""
Setup script for Rental Contract RAG Demo
This script helps set up the project environment using Poetry.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, shell=False):
    """Run a command and return success status."""
    try:
        result = subprocess.run(command, shell=shell, check=True, capture_output=True, text=True)
        print(f"✅ {' '.join(command) if not shell else command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {' '.join(command) if not shell else command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is 3.12 or higher."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not supported")
        print("   Please install Python 3.12 or higher")
        return False

def check_poetry():
    """Check if Poetry is installed."""
    return shutil.which("poetry") is not None

def setup_with_poetry():
    """Set up the project using Poetry."""
    print("\n🔧 Setting up with Poetry...")
    
    if not check_poetry():
        print("❌ Poetry not found. Installing Poetry...")
        if sys.platform.startswith("win"):
            # Windows installation
            command = 'powershell -Command "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"'
            if not run_command(command, shell=True):
                return False
        else:
            # Unix-like systems
            command = "curl -sSL https://install.python-poetry.org | python3 -"
            if not run_command(command, shell=True):
                return False
    
    # Install dependencies
    if not run_command(["poetry", "install"]):
        return False
    
    print("✅ Poetry setup complete!")
    print("\n📝 Next steps:")
    print("   1. Copy .env.example to .env and add your API keys")
    print("   2. Run: poetry shell")
    print("   3. Run: poetry run python src/app.py")
    return True

def setup_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from .env.example")
        print("   ⚠️  Please edit .env and add your API keys!")
        return True
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ .env.example not found")
        return False

def main():
    """Main setup function."""
    print("🚀 Rental Contract RAG Demo Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup environment file
    setup_env_file()
    
    # Setup with Poetry
    success = setup_with_poetry()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("\n📚 Don't forget to:")
        print("   - Add your OpenAI API key to .env")
        print("   - Check the README.md for detailed instructions")
        print("   - Run tests with: poetry run pytest")
        print("\n🐳 Alternative: Use Docker")
        print("   - docker-compose up")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        print("\n💡 Alternative setup options:")
        print("   - Use Docker: docker-compose up")
        print("   - Install Poetry manually and run: poetry install")
        sys.exit(1)

if __name__ == "__main__":
    main()