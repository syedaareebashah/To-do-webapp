"""
Simple test server to see errors
"""

import os
os.environ['DATABASE_URL'] = 'sqlite:///./todo_chatbot.db'

from src.app.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)