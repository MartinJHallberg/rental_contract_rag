import os
from dash import Dash
import dash_bootstrap_components as dbc

from ui.layout import create_layout
from ui.callbacks import register_callbacks
from rag import RAGChain


def create_app():
    """Create and configure the Dash app"""
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Initialize RAG chain
    rag_chain = RAGChain()

    # Set layout
    app.layout = create_layout()

    # Register callbacks
    register_callbacks(app, rag_chain)

    return app


if __name__ == "__main__":
    app = create_app()

    # Get configuration from environment variables
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    host = os.getenv("DASH_HOST", "0.0.0.0")
    port = int(os.getenv("DASH_PORT", "8050"))

    # Determine the display URL based on the host
    if host == "0.0.0.0":
        display_host = "localhost"
    else:
        display_host = host

    print("\n" + "=" * 60)
    print("🏠 Rental Contract Validator")
    print("=" * 60)
    print(f"🌐 Server: http://{display_host}:{port}/")
    print(f"🔧 Debug: {'ON' if debug_mode else 'OFF'}")
    print(f"📡 Binding: {host}:{port}")
    print("=" * 60)

    app.run(debug=debug_mode, host=host, port=port)
