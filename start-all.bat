@echo off
echo ================================================
echo   Deep Research Agent - Starting Both Servers
echo ================================================
echo.

set "PROJECT_ROOT=c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"

echo [1/2] Starting Python Backend API Server...
echo      Port: 7863
echo      Docs: http://localhost:7863/docs
echo.

start "Deep Research - Backend API" cmd /k "cd /d "%PROJECT_ROOT%" && poetry run python deep_research\api_server.py"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Next.js Frontend...
echo      Port: 3000
echo      URL: http://localhost:3000
echo.

start "Deep Research - Frontend" cmd /k "cd /d "%PROJECT_ROOT%\deep_research\frontend" && npm run dev"

echo.
echo ================================================
echo   Both servers are starting in separate windows
echo ================================================
echo.
echo Backend API: http://localhost:7863
echo Frontend:    http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul
