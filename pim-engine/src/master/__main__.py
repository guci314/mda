"""Master Controller Entry Point"""

import uvicorn
from .app import create_app

# Print startup banner
print("""
╔═══════════════════════════════════════════════╗
║     PIM Engine Master Controller v2.0.0       ║
║   Multi-Process Model Instance Management     ║
╚═══════════════════════════════════════════════╝
    """)

# Create app
app = create_app()

# Run server
if __name__ == "__main__":
    print("Starting master controller on http://0.0.0.0:8000")
    print("API Docs: http://0.0.0.0:8000/docs")
    print("Health: http://0.0.0.0:8000/health")
    print("\nPress CTRL+C to stop\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)