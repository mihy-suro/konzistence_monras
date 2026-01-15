"""
Callbacks package for MRS Viewer.

Modular callback structure:
- filters: Filter dropdown updates
- selection: Graph selection handling
- reference: Reference period line positioning
- main_content: Main scatter plot and table rendering
"""
from .filters import register_filter_callbacks
from .selection import register_selection_callbacks
from .reference import register_reference_callbacks
from .main_content import register_main_callbacks


def register_callbacks(app):
    """Register all callbacks with the Dash app."""
    register_filter_callbacks(app)
    register_selection_callbacks(app)
    register_reference_callbacks(app)
    register_main_callbacks(app)
