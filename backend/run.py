"""
Simple script to run the FastAPI application.
This handles the import path issues.
"""
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
