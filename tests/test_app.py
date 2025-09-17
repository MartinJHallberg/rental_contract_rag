import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_rag_chain():
    """Mock RAGChain to avoid OpenAI API key requirement."""
    with patch("app.RAGChain") as mock:
        mock.return_value = MagicMock()
        yield mock


def test_app_starts(mock_rag_chain):
    """Test that the Dash app can be created without errors."""
    from app import create_app

    # Create the app instance
    app = create_app()

    # Verify it's a Dash app
    assert app is not None
    assert hasattr(app, "layout")
    assert hasattr(app, "run")


def test_create_app_function_exists():
    """Test that the create_app function exists and is callable."""
    from app import create_app

    assert callable(create_app)


def test_app_has_layout(mock_rag_chain):
    """Test that the app has a layout configured."""
    from app import create_app

    app = create_app()

    # Check that layout is set
    assert app.layout is not None
