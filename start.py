#!/usr/bin/env python3
"""
Startup script for Railway deployment
Reads PORT from environment and starts uvicorn
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting SuperAgent on port {port}")
    
    uvicorn.run(
        "api.index:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
