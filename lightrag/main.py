#!/usr/bin/env python3
"""
Main entry point for LightRAG service
"""

import sys
import os

# Add the parent directory to Python path to avoid import conflicts
sys.path.insert(0, '/app')

# Now import and run our API
from lightrag_service.api import app
import uvicorn

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8080"))
    
    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )