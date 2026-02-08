# 🔍 Debug the 404 Error

## Step 1: Check Browser Console

1. Open your browser at http://localhost:3000
2. Press **F12** to open Developer Tools
3. Click the **Console** tab
4. Click the **Network** tab
5. Try to send a chat message
6. Look for any **red** failed requests

## Step 2: Find the 404 Request

In the Network tab, look for requests with status **404**.

**Tell me:**
- What is the **exact URL** that's returning 404?
- Is it something like:
  - `http://localhost:8000/api/...` (wrong port)
  - `http://localhost:8001/api/...` (correct port)
  - `http://localhost:8001/auth/...` (auth endpoint)
  - Something else?

## Step 3: Check API URL

Open browser console and type:
```javascript
console.log(process.env.NEXT_PUBLIC_API_URL)
```

**What does it show?**
- Should be: `http://localhost:8001`
- If it shows: `http://localhost:8000` or `undefined` - frontend didn't restart properly

## Step 4: Verify Frontend Restart

Did you:
1. Press Ctrl+C in the frontend terminal?
2. Run `npm run dev` again?
3. Wait for "ready started server" message?
4. Hard refresh the browser (Ctrl+Shift+R)?

---

## Quick Test

Run this in your browser console:
```javascript
fetch('http://localhost:8001/health')
  .then(r => r.json())
  .then(d => console.log('Backend:', d))
```

This should show the backend is reachable.

---

**Please tell me:**
1. The exact 404 URL from Network tab
2. What the console.log shows for API URL
3. Did you fully restart the frontend?
