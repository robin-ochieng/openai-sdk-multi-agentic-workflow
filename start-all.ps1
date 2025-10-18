# Deep Research Agent - Start All Servers
# This script starts both the Python backend and Next.js frontend

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Deep Research Agent - Starting All Servers" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"

# Function to check if a port is in use
function Test-Port {
    param($Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
    return $connection.TcpTestSucceeded
}

# Check if backend is already running
if (Test-Port 7863) {
    Write-Host "⚠️  Backend already running on port 7863" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "🚀 [1/2] Starting Python Backend API Server..." -ForegroundColor Green
    Write-Host "      Port: 7863" -ForegroundColor White
    Write-Host "      Docs: http://localhost:7863/docs" -ForegroundColor White
    Write-Host ""
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot'; poetry run python deep_research\api_server.py" -WindowStyle Normal
    
    # Wait for backend to start
    Write-Host "   Waiting for backend to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    if (Test-Port 7863) {
        Write-Host "   ✅ Backend started successfully!" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Backend may still be starting..." -ForegroundColor Yellow
    }
    Write-Host ""
}

# Check if frontend is already running
if (Test-Port 3000) {
    Write-Host "⚠️  Frontend already running on port 3000" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "🌐 [2/2] Starting Next.js Frontend..." -ForegroundColor Green
    Write-Host "      Port: 3000" -ForegroundColor White
    Write-Host "      URL:  http://localhost:3000" -ForegroundColor White
    Write-Host ""
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\deep_research\frontend'; npm run dev" -WindowStyle Normal
    
    # Wait for frontend to start
    Write-Host "   Waiting for frontend to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    
    if (Test-Port 3000) {
        Write-Host "   ✅ Frontend started successfully!" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Frontend may still be starting..." -ForegroundColor Yellow
    }
    Write-Host ""
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Servers Started!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:7863" -ForegroundColor Cyan
Write-Host "   API Docs: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:7863/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend:    " -NoNewline -ForegroundColor White
Write-Host "http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tip: Open http://localhost:3000 in your browser" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to close this window (servers will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
