"""
Server Entry Point

Production entry point for the backend API.

Team: DevOps
"""

import sys
from pathlib import Path

# Add packages to path for 'from packages.* import ...'
root = Path(__file__).parent.parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Import and run the app
from packages.api.src import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "packages.api.src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable in production
    )
