# 🐛 HTTP 500 Error - Troubleshooting Guide

## Problem
The Deep Research Agent frontend is showing **"HTTP error! status: 500"** because it cannot connect to the Python backend API server.

## Root Cause
The **Python FastAPI backend server is NOT running** on port 7863. The Next.js frontend is trying to connect to `http://localhost:7863/api/research` but getting a connection error, which results in a 500 status.

## Solution Steps

### ✅ Step 1: Start the Python Backend API Server

**Option A: Using the batch file (EASIEST)**
```bash
# Open a NEW terminal and run:
cd "c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"
.\start-backend.bat
```

**Option B: Using Poetry directly**
```bash
# Open a NEW terminal and run:
cd "c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"
poetry run python deep_research/api_server.py
```

**Option C: Using Uvicorn**
```bash
# Open a NEW terminal and run:
cd "c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"
poetry run uvicorn deep_research.api_server:app --host 0.0.0.0 --port 7863 --reload
```

### ✅ Step 2: Verify Backend is Running

You should see output like:
```
🚀 Starting Deep Research Agent API Server
📍 API: http://localhost:7863
📍 Docs: http://localhost:7863/docs
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7863
```

You can also check:
```bash
# In PowerShell:
netstat -ano | findstr :7863

# You should see:
# TCP    0.0.0.0:7863    0.0.0.0:0    LISTENING    [PID]
```

### ✅ Step 3: Test the Backend API

Open your browser and visit:
- **API Docs:** http://localhost:7863/docs
- **Health Check:** http://localhost:7863/health
- **Root:** http://localhost:7863/

If these work, the backend is running correctly!

### ✅ Step 4: Refresh the Frontend

Go back to your browser with the Deep Research Agent frontend and:
1. Refresh the page (F5 or Ctrl+R)
2. Enter a research query (minimum 12 characters)
3. Click "Start Research"

The error should be gone! ✨

## Architecture Overview

```
┌─────────────────────┐
│   Next.js Frontend  │
│   (Port 3000)       │
│                     │
│   User Interface    │
└──────────┬──────────┘
           │
           │ HTTP POST /api/research
           ▼
┌─────────────────────┐
│  Next.js API Route  │
│  /api/research      │
│                     │
│  Proxy Layer        │
└──────────┬──────────┘
           │
           │ Forwards to http://localhost:7863
           ▼
┌─────────────────────┐
│  Python FastAPI     │ ◄── THIS WAS NOT RUNNING!
│  (Port 7863)        │
│                     │
│  Research Agents    │
└─────────────────────┘
```

## Why This Happened

The frontend expects the backend to be running, but:
1. The Python backend server was not started
2. Port 7863 was not listening
3. The Next.js API route tried to forward the request to `http://localhost:7863`
4. Connection failed → 500 Internal Server Error

## Prevention

**Always run BOTH servers:**

### Terminal 1: Backend (Python)
```bash
cd "c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"
poetry run python deep_research/api_server.py
```

### Terminal 2: Frontend (Next.js)
```bash
cd "c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents\deep_research\frontend"
npm run dev
```

## Quick Start Commands

I've created a batch file for easy backend startup:

**Windows:**
```bash
.\start-backend.bat
```

**Alternative - Use existing PowerShell script (after fixing):**
```powershell
.\start-api-server.ps1
```

## Environment Variables

The Next.js API route uses this environment variable:
```env
PYTHON_API_URL=http://localhost:7863
```

If the backend runs on a different port, update:
```bash
# In frontend/.env.local
PYTHON_API_URL=http://localhost:YOUR_PORT
```

## Debugging Tips

### Check if backend is running:
```powershell
# PowerShell
Get-Process | Where-Object { $_.ProcessName -like "*python*" }

# Or check port
netstat -ano | findstr :7863
```

### Check backend logs:
Look at the terminal where you started `api_server.py` - any errors will show there.

### Check frontend API route logs:
Look at the Next.js dev server terminal - it logs requests to `/api/research`

### Test backend directly:
```bash
# Using curl
curl -X POST http://localhost:7863/api/research \
  -H "Content-Type: application/json" \
  -d '{"query": "test query for debugging purposes"}'

# Using PowerShell
Invoke-RestMethod -Uri "http://localhost:7863/api/research" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query": "test query for debugging purposes"}'
```

## Common Issues

### Issue 1: Port Already in Use
```
Error: [Errno 10048] address already in use
```
**Solution:** Another process is using port 7863
```bash
# Find the process
netstat -ano | findstr :7863
# Kill it
taskkill /PID <PID_NUMBER> /F
```

### Issue 2: Poetry Not Found
```
poetry: command not found
```
**Solution:** Install Poetry or use Python directly
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python deep_research/api_server.py
```

### Issue 3: Missing Dependencies
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:** Install missing packages
```bash
poetry install
# or
pip install fastapi uvicorn
```

### Issue 4: CORS Errors
If you see CORS errors, ensure the backend's CORS middleware includes your frontend URL:
```python
# In api_server.py
allow_origins=["http://localhost:3000", "http://localhost:3001"]
```

## Success Indicators

✅ Backend terminal shows: `INFO: Uvicorn running on http://0.0.0.0:7863`  
✅ Frontend shows the research form without errors  
✅ Clicking "Start Research" triggers the research process  
✅ Timeline, Console, and Evidence sections appear  
✅ No HTTP 500 errors in browser console  

## Next Steps

Once the backend is running:
1. Test the research functionality
2. Try different queries
3. Check the agent console for streaming logs
4. View the generated reports

Need help? Check the API documentation at: http://localhost:7863/docs

---

**Created:** October 18, 2025  
**Issue:** HTTP 500 - Backend not running  
**Solution:** Start Python API server on port 7863  
