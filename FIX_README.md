# 🐛 FIXED: HTTP 500 Error

## Problem
❌ **"HTTP error! status: 500"** in the Deep Research Agent frontend

## Root Cause
The **Python backend API server was not running** on port 7863.

## ✅ Quick Fix

### Option 1: Start All Servers (EASIEST) ⭐
Double-click or run:
```bash
.\start-all.bat
```

Or in PowerShell:
```powershell
.\start-all.ps1
```

This will start BOTH:
- ✅ Python Backend (Port 7863)
- ✅ Next.js Frontend (Port 3000)

### Option 2: Start Backend Only
```bash
.\start-backend.bat
```

Or:
```bash
cd "c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"
poetry run python deep_research/api_server.py
```

## Verify It's Working

1. **Check Backend:** http://localhost:7863/docs (should show API docs)
2. **Check Frontend:** http://localhost:3000 (should show the app)
3. **Test Research:** Enter a query and click "Start Research"

## What Was the Issue?

```
Frontend (Next.js) → Tries to connect to Backend (Python) → 💥 NOT RUNNING!
    Port 3000                    Port 7863                   = 500 Error
```

**Solution:** Start the backend first, then frontend works! ✨

## Files Created to Help You

1. ✅ `start-all.bat` - Start both servers (Windows batch)
2. ✅ `start-all.ps1` - Start both servers (PowerShell)
3. ✅ `start-backend.bat` - Start backend only
4. ✅ `TROUBLESHOOTING_500_ERROR.md` - Full troubleshooting guide

## Still Having Issues?

See the full guide: [TROUBLESHOOTING_500_ERROR.md](./TROUBLESHOOTING_500_ERROR.md)

---

**Fixed:** October 18, 2025  
**Resolution:** Backend server startup scripts created
