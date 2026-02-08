import os
import uvicorn
from src.app.main import app

# Set the database URL
os.environ['DATABASE_URL'] = 'sqlite:///./todo_chatbot.db'

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info", reload=False)