"""
Root entrypoint for Streamlit Community Cloud deployment.
Allows Streamlit Cloud to automatically detect and run the application.
"""

import os
import sys

# Ensure root directory is on the Python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Run app
from app.app import *
