#!/usr/bin/env python3
"""
Development server startup script for AI Quiz Builder API
"""
import uvicorn
import os

if __name__ == "__main__":
    # Set development environment
    os.environ.setdefault("DEBUG", "True")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 