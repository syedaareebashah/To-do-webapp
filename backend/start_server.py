import os
from app.main import app

# Set the database URL
os.environ['DATABASE_URL'] = 'sqlite:///./todo_web_app.db'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )