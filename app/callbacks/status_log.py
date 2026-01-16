"""
Status log panel callbacks.

Handles logging of application events and displaying them in the status panel.
Provides a centralized way to track user actions and data changes.
"""
from datetime import datetime
from typing import Optional

import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, no_update, callback_context

from .. import ids


# Log levels with icons and colors
LOG_ICONS = {
    "info": ("bi-info-circle", "text-info"),
    "success": ("bi-check-circle", "text-success"),
    "warning": ("bi-exclamation-triangle", "text-warning"),
    "error": ("bi-x-circle", "text-danger"),
}

MAX_LOG_ENTRIES = 100


def create_log_entry(timestamp: str, message: str, level: str = "info") -> html.Div:
    """Create a styled log entry component."""
    icon_class, color_class = LOG_ICONS.get(level, LOG_ICONS["info"])
    
    return html.Div(
        [
            html.Span(timestamp, className="text-muted me-2", style={"fontSize": "0.75rem", "fontFamily": "monospace"}),
            html.I(className=f"bi {icon_class} {color_class} me-1"),
            html.Span(message, className=color_class, style={"fontSize": "0.85rem"}),
        ],
        className="py-1 border-bottom border-secondary",
        style={"borderBottom": "1px solid #444"},
    )


def add_log_entry(store_data: dict, message: str, level: str = "info") -> dict:
    """Add a new log entry to the store data."""
    if store_data is None:
        store_data = {"entries": []}
    
    entries = store_data.get("entries", [])
    
    # Create new entry
    new_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "message": message,
        "level": level,
    }
    
    # Add to front (newest first)
    entries.insert(0, new_entry)
    
    # Keep only last MAX_LOG_ENTRIES
    if len(entries) > MAX_LOG_ENTRIES:
        entries = entries[:MAX_LOG_ENTRIES]
    
    return {"entries": entries}


def render_log_entries(store_data: dict) -> list:
    """Render all log entries from store data."""
    if not store_data or not store_data.get("entries"):
        return [
            html.Div(
                "Žádné záznamy v logu.",
                className="text-muted text-center py-3",
                style={"fontSize": "0.85rem"},
            )
        ]
    
    return [
        create_log_entry(
            entry["timestamp"],
            entry["message"],
            entry.get("level", "info"),
        )
        for entry in store_data["entries"]
    ]


def register_status_log_callbacks(app):
    """Register callbacks for status log functionality."""
    
    @app.callback(
        Output(ids.STATUS_LOG_CONTAINER, "children"),
        Input(ids.STORE_STATUS_LOG, "data"),
    )
    def update_log_display(store_data):
        """Update the log display when store changes."""
        return render_log_entries(store_data)
    
    @app.callback(
        Output(ids.STORE_STATUS_LOG, "data", allow_duplicate=True),
        Input(ids.BTN_CLEAR_STATUS_LOG, "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_log(n_clicks):
        """Clear all log entries."""
        if not n_clicks:
            return no_update
        return {"entries": []}
    
    # Initialize log on app start
    @app.callback(
        Output(ids.STORE_STATUS_LOG, "data", allow_duplicate=True),
        Input(ids.STORE_STATUS_LOG, "modified_timestamp"),
        State(ids.STORE_STATUS_LOG, "data"),
        prevent_initial_call="initial_duplicate",
    )
    def initialize_log(ts, data):
        """Initialize log with welcome message if empty."""
        if data is None or not data.get("entries"):
            return add_log_entry(
                {"entries": []},
                "Aplikace spuštěna. Vyberte dataset pro začátek.",
                "info"
            )
        return no_update
