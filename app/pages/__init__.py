"""
MRS Viewer - Multi-page application pages.
"""
from .home import create_home_page
from .docs import create_docs_page
from .config_editor import create_config_page

__all__ = ["create_home_page", "create_docs_page", "create_config_page"]
