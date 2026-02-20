#!/usr/bin/env python
"""Run the Chat Website API Wrapper Server"""
import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    # Read from environment or use defaults
    use_selenium = os.getenv("USE_SELENIUM", "false").lower() == "true"
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    chat_url = os.getenv("CHAT_WEBSITE_URL", "https://example-chat.com")
    
    print("=" * 60)
    print("🚀 Chat Website API Wrapper")
    print("=" * 60)
    print(f"Target: {chat_url}")
    print(f"Mode: {'Selenium (browser automation)' if use_selenium else 'HTTP (reverse-engineered)'}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"OpenAPI Docs: http://{host}:{port}/docs")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
