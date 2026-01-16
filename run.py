#!/usr/bin/env python
"""
MRS Viewer - Run Script

Usage:
    python run.py           # Development mode (debug=True)
    python run.py --prod    # Production mode (debug=False)
"""
import sys

from app.app import app
from app.config import config

if __name__ == "__main__":
    # Allow --prod flag to override config debug setting
    debug = config.server.debug if "--prod" not in sys.argv else False
    port = config.server.port
    host = config.server.host
    
    print(f"\n{'=' * 50}")
    print("  MRS Viewer")
    print(f"{'=' * 50}")
    print(f"  Mode: {'Development' if debug else 'Production'}")
    print(f"  URL:  http://{host}:{port}/")
    print(f"{'=' * 50}\n")
    
    app.run(debug=debug, port=port, host=host)