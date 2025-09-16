import pytest
import sys
import os
from app import create_app


def test_app_starts():
    """Test that the Dash app can be created without errors."""
    try:
        # Create the app instance
        app = create_app()

        # Verify it's a Dash app
        assert app is not None
        assert hasattr(app, "layout")
        assert hasattr(app, "run")

    except ImportError as e:
        pytest.fail(f"Failed to import app: {e}")
    except Exception as e:
        pytest.fail(f"App failed to start: {e}")


def test_create_app_function_exists():
    """Test that the create_app function exists and is callable."""
    try:
        assert callable(create_app)

    except ImportError as e:
        pytest.fail(f"Failed to import create_app function: {e}")


def test_app_has_layout():
    """Test that the app has a layout configured."""
    try:
        app = create_app()

        # Check that layout is set
        assert app.layout is not None

    except Exception as e:
        pytest.fail(f"App layout test failed: {e}")
