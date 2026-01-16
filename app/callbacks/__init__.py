"""
Callbacks package for MRS Viewer.

Modular callback structure:
- filters: Filter dropdown updates
- selection: Graph selection handling
- reference: Reference period line positioning
- main_content: Main scatter plot and table rendering
- side_charts: Side charts (boxplot, etc.)
- routing: Page routing and navigation
- suspicious: Suspicious records basket
- status_log: Status log panel
"""
from .filters import register_filter_callbacks
from .selection import register_selection_callbacks
from .reference import register_reference_callbacks
from .main_content import register_main_callbacks
from .side_charts import register_side_charts_callbacks
from .routing import register_routing_callbacks
from .suspicious import register_suspicious_callbacks
from .status_log import register_status_log_callbacks


def register_callbacks(app):
    """Register all callbacks with the Dash app."""
    register_routing_callbacks(app)  # Must be first for page routing
    register_filter_callbacks(app)
    register_selection_callbacks(app)
    register_reference_callbacks(app)
    register_main_callbacks(app)
    register_side_charts_callbacks(app)
    register_suspicious_callbacks(app)
    register_status_log_callbacks(app)
