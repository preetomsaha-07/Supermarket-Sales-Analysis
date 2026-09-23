"""
=============================================================================
Vercel Serverless Function Entry Point
=============================================================================
This file acts as the serverless bridge between Vercel and our Flask application.
Vercel's Python runtime automatically imports 'app' (WSGI application)
from this file and routes incoming web requests to it.
"""

import sys
import os

# Ensure the root project directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import the Flask application instance
from backend.app import app

# Vercel WSGI entry point
# In Vercel, the exposed 'app' variable is invoked for all incoming HTTP requests
if __name__ == "__main__":
    app.run()
