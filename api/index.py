"""
Vercel Serverless Entrypoint for Hermes Agent & Mission Control API.
"""

import sys
from pathlib import Path

# Ensure project root is in Python module search path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Expose the FastAPI app object for Vercel Serverless Function runtime
from hermes_cli.web_server import app
