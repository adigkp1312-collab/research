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
    import os
    import uvicorn
    
    # Cloud Run provides PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "packages.api.src.app:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable in production
    )
