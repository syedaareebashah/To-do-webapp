# START THE TODO CHAT API BACKEND

## Current Situation

Your frontend chat UI is ready, but the backend on port 8000 is running **Kiro Gateway** instead of the **Todo Chat API** we integrated.

## Solution: Start the Todo Chat API

### Option 1: Start on a Different Port (Recommended)

Open a new terminal and run:

```bash
cd C:\Users\mehre\Downloads\hackathonnII\Hackathon_II\phase_III
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8001
```

Then update your frontend to use port 8001:

**Create/Edit**: `frontend/.env.local`
```
NEXT_PUBLIC_API_URL=http://localhost:8001
```

Restart your frontend:
```bash
cd frontend
npm run dev
```

### Option 2: Replace Kiro Gateway (Alternative)

If you want to use port 8000 for the Todo Chat API:

1. **Stop Kiro Gateway**:
   - Find the process: `tasklist | findstr python`
   - Kill it: `taskkill /PID <process_id> /F`

2. **Start Todo Chat API**:
```bash
cd C:\Users\mehre\Downloads\hackathonnII\Hackathon_II\phase_III
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Test with Kiro Gateway (Advanced)

Kiro Gateway has a chat completions endpoint at `/v1/chat/completions`. You could adapt the frontend to use this, but it would require code changes.

## Quick Test

After starting the Todo Chat API, verify it's working:

```bash
curl http://localhost:8001/
```

Expected response:
```json
{
  "message": "Welcome to Todo AI Chatbot API",
  "status": "running",
  "version": "1.0.0"
}
```

## Then Test Your Chatbot

1. Open http://localhost:3000
2. Sign in
3. Click "Show AI Chat"
4. Type: "Add a task to buy groceries"
5. Watch it work!

---

**Recommendation**: Use Option 1 (port 8001) to keep both services running.
