# How to Run the Todo Backend

## Current Status
The Todo backend is currently running on port 8001:
- Health check: http://localhost:8001/health
- API documentation: http://localhost:8001/docs

## If You Need to Restart the Backend

### 1. Stop Current Process (if needed)
```bash
# Find the process ID
tasklist | findstr uvicorn
# Or specifically for the Python process running the backend
tasklist | findstr python
```

```bash
# Kill the specific process (replace PID with actual process ID)
taskkill /F /T /PID <PID>
```

### 2. Start the Backend Server
```bash
# Navigate to the project directory
cd C:\Users\mehre\Downloads\hackathonnII\Hackathon_II\phase_III

# Make sure dependencies are installed
pip install -r requirements.txt

# Initialize the database (if not already done)
python -c "from src.database.session import init_db; init_db()"

# Start the backend server
uvicorn src.app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Alternative: Run on Different Port
If port 8001 is busy, you can run on a different port:
```bash
uvicorn src.app.main:app --host 0.0.0.0 --port 8002 --reload
```

## Backend Features
- **Task Management**: Add, list, complete, and delete tasks
- **MCP Integration**: Model Context Protocol tools for AI agent
- **Database**: PostgreSQL with proper session management
- **Authentication**: Protected endpoints with user isolation

## API Endpoints
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `POST /api/{user_id}/chat` - Main chat endpoint with task operations

## Testing the Backend
Once running, you can test with:
```bash
curl http://localhost:8001/health
```

## Troubleshooting
- If you get "Address already in use" error, kill the existing process or use a different port
- If you get database errors, make sure to run the init_db command
- If you get dependency errors, run pip install -r requirements.txt

## Stopping the Backend
Press Ctrl+C in the terminal where the server is running, or use taskkill command as shown above.