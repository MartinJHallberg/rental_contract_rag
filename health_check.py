#!/usr/bin/env python3
"""
Health check script for Rental Contract RAG Demo
Run this script to verify that everything is set up correctly.
"""

import sys
import os
import importlib
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(
            f"❌ Python {version.major}.{version.minor}.{version.micro} (requires >= 3.12)"
        )
        return False


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        "dash",
        "langchain",
        "openai",
        "pandas",
        "pypdf",
        "pdfplumber",
        "chromadb",
        "sentence_transformers",
    ]

    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (not installed)")
            missing_packages.append(package)

    return len(missing_packages) == 0


def check_environment_file():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Create one from .env.example and add your API keys")
        return False

    print("✅ .env file exists")

    # Check for required variables
    from dotenv import load_dotenv

    load_dotenv()

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("⚠️  OPENAI_API_KEY not set in .env")
        return False
    else:
        print("✅ OPENAI_API_KEY configured")

    return True


def check_data_directories():
    """Check if required data directories exist."""
    directories = ["src/data", "src/data/cache", "src/data/vector_stores"]

    all_exist = True
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory} (missing)")
            all_exist = False

    return all_exist


def check_imports():
    """Check if the main modules can be imported."""
    sys.path.insert(0, "src")

    modules = ["config", "contract_loader", "rag", "data_loading"]

    all_imported = True
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module} ({str(e)})")
            all_imported = False

    return all_imported


def main():
    """Run all health checks."""
    print("🏥 Rental Contract RAG Health Check")
    print("=" * 40)

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_environment_file),
        ("Data Directories", check_data_directories),
        ("Module Imports", check_imports),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        result = check_func()
        results.append(result)

    print("\n" + "=" * 40)

    if all(results):
        print("🎉 All checks passed! Your setup is ready.")
        print("\n📝 Next steps:")
        print("   1. Run: python src/app.py")
        print("   2. Open: http://localhost:8050")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n💡 Need help? Check:")
        print("   - README.md for setup instructions")
        print("   - .env.example for configuration")
        print("   - pyproject.toml for dependencies")
        return 1


if __name__ == "__main__":
    sys.exit(main())
