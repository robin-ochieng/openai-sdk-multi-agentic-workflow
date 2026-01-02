# Start Both Servers - Quick Start Script

Write-Host "Starting Deep Research Agent System..." -ForegroundColor Cyan

$projectRoot = "c:\Users\Robin Ochieng.BEN-ODHIAMBO\OneDrive - Kenbright\Gig\AI Agents\Projects\Deep Research Agent\openai-sdk-multi-agentic-workflow"
$frontendPath = Join-Path $projectRoot "deep_research\frontend"
$venvPath = Join-Path $projectRoot "venv\Scripts\Activate.ps1"

# Check virtual environment
if (-not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found! Please create it first." -ForegroundColor Red
    exit 1
}

# Check Node
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js not found!" -ForegroundColor Red
    exit 1
}

# Check frontend deps
if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location $frontendPath
    npm install
    Pop-Location
}

# Start Backend
Write-Host "Starting Python API Backend..." -ForegroundColor Cyan
$backendCmd = "Set-Location '$projectRoot'; & '$venvPath'; python deep_research/api_server.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$backendCmd"

# Start Frontend
Write-Host "Starting Next.js Frontend..." -ForegroundColor Cyan
$frontendCmd = "Set-Location '$frontendPath'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$frontendCmd"

Write-Host "Waiting for services to start..."
Start-Sleep -Seconds 10

Write-Host "Opening browser..."
Start-Process "http://localhost:3000"

Write-Host "Done! Frontend running at http://localhost:3000" -ForegroundColor Green
