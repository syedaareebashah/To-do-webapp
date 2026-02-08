import os
import sys

# Add the backend directory to the path
sys.path.insert(0, '.')

# Set the database URL
os.environ['DATABASE_URL'] = 'sqlite:///./todo_web_app.db'

from app.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)