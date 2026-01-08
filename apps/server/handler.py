"""
Lambda Handler for FastAPI Application

Uses Mangum to adapt FastAPI to Lambda event format.

Team: DevOps
"""

import sys
from pathlib import Path

# Add project root to Python path for package imports
# This allows 'from packages.* import ...' to work
root = Path(__file__).parent.parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from mangum import Mangum
from packages.api.src import app

# Create Mangum adapter
handler = Mangum(app, lifespan="off")
