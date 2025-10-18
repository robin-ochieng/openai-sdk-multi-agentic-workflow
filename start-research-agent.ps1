# Start Both Servers - Quick Start Script
# This script starts both the Python backend and Next.js frontend

Write-Host "🚀 Starting Deep Research Agent System" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Poetry is installed
Write-Host "📦 Checking Poetry installation..." -ForegroundColor Yellow
$poetryCheck = Get-Command poetry -ErrorAction SilentlyContinue
if (-not $poetryCheck) {
    Write-Host "❌ Poetry not found! Please install Poetry first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Poetry found" -ForegroundColor Green
Write-Host ""

# Check if Node.js is installed
Write-Host "📦 Checking Node.js installation..." -ForegroundColor Yellow
$nodeCheck = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCheck) {
    Write-Host "❌ Node.js not found! Please install Node.js first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js found ($(node --version))" -ForegroundColor Green
Write-Host ""

# Get project root
$projectRoot = "c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"
$frontendPath = Join-Path $projectRoot "deep_research\frontend"

# Check if frontend dependencies are installed
if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Write-Host "📦 Installing frontend dependencies (first time setup)..." -ForegroundColor Yellow
    Set-Location $frontendPath
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# Start Python backend in new terminal
Write-Host "🐍 Starting Python API Backend (port 7863)..." -ForegroundColor Cyan
$backendScript = @"
Write-Host '🐍 Python API Backend Server' -ForegroundColor Cyan
Write-Host '============================' -ForegroundColor Cyan
Set-Location '$projectRoot'
poetry run python deep_research/api_server.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

Write-Host "✅ Python backend starting in new terminal" -ForegroundColor Green
Write-Host ""

# Wait a bit for backend to start
Write-Host "⏳ Waiting for backend to initialize (5 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host ""

# Start Next.js frontend in new terminal
Write-Host "⚡ Starting Next.js Frontend (port 3000)..." -ForegroundColor Cyan
$frontendScript = @"
Write-Host '⚡ Next.js Frontend Server' -ForegroundColor Cyan
Write-Host '=========================' -ForegroundColor Cyan
Set-Location '$frontendPath'
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host "✅ Next.js frontend starting in new terminal" -ForegroundColor Green
Write-Host ""

# Wait a bit for frontend to start
Write-Host "⏳ Waiting for frontend to initialize (10 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host ""

# Open browser
Write-Host "🌐 Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "✨ Deep Research Agent is Ready!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "📍 Backend:  http://localhost:7863" -ForegroundColor White
Write-Host ""
Write-Host "💡 To stop the servers:" -ForegroundColor Yellow
Write-Host "   - Close the terminal windows" -ForegroundColor Yellow
Write-Host "   - Or press Ctrl+C in each terminal" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   - Frontend: deep_research/frontend/README.md" -ForegroundColor White
Write-Host "   - Setup Guide: deep_research/frontend/COMPLETE_SETUP_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "Happy researching! 🎉" -ForegroundColor Green
Write-Host ""
