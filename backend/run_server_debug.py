import os
import sys
import threading
import time

# Add the backend directory to the path
sys.path.insert(0, '.')

# Set the database URL
os.environ['DATABASE_URL'] = 'sqlite:///./todo_web_app.db'

def run_server():
    from app.main import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    print("Starting server...")
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait a bit and then check if it's running
    time.sleep(5)
    print("Server should be running on port 8000")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server...")
        sys.exit(0)