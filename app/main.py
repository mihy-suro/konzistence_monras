"""
Entry point pro MonRaS Dash aplikaci.

Tento modul:
1. Importuje centrální Dash instanci ze server.py
2. Registruje všechny callbacks (import modulů je registruje)
3. Nastavuje hlavní layout
4. Spouští vývojový server

Spuštění:
    uv run python -m app.main
    
    nebo:
    
    cd app && uv run python main.py
"""

from app.server import app
from app.layouts.main_layout import create_layout

# Registrace všech callbacks importem modulů
# (dekorátory @app.callback se vykonají při importu)
from app.callbacks import (  # noqa: F401
    upload_callbacks,
    filter_callbacks,
    chart_callbacks,
    outlier_callbacks,
)

# Nastavení hlavního layoutu
app.layout = create_layout()


def main():
    """Spustí vývojový Dash server."""
    app.run_server(
        debug=True,
        port=8050,
        host="127.0.0.1",
    )


if __name__ == "__main__":
    main()
