#!/usr/bin/env python3
"""
Government Data API - Launch script
"""
import uvicorn
import os

if __name__ == "__main__":
    # Install dependencies
    print("🚀 Starting Government Data API...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )