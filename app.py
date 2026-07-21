import os
import sys
import subprocess
import uvicorn

# Setup the database migrations before starting the server
print("Running Alembic migrations...")
os.environ["DATABASE_URL"] = "sqlite:///./sqlite.db"
os.chdir("backend")
try:
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    print("Migrations completed successfully.")
except Exception as e:
    print(f"Migration error (ignoring if DB exists): {e}")

# Revert to root and add backend to python path so it can find the modules
os.chdir("..")
sys.path.append(os.path.abspath("backend"))

# Import the FastAPI app from the backend directory
from backend.main import app

if __name__ == "__main__":
    # Hugging Face Spaces (Gradio) defaults to port 7860
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
