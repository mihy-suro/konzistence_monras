#!/usr/bin/env python
"""
MRS Viewer - Run Script

Usage:
    python run.py           # Development mode (debug=True)
    python run.py --prod    # Production mode (debug=False)
"""
import sys

from app.app import app

if __name__ == "__main__":
    debug = "--prod" not in sys.argv
    port = 8050
    
    print(f"\n{'=' * 50}")
    print("  MRS Viewer")
    print(f"{'=' * 50}")
    print(f"  Mode: {'Development' if debug else 'Production'}")
    print(f"  URL:  http://localhost:{port}/")
    print(f"{'=' * 50}\n")
    
    app.run(debug=debug, port=port)
