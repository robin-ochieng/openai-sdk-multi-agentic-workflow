# Start Both Servers - Quick Start Script

Write-Host "Starting Deep Research Agent System..." -ForegroundColor Cyan

# Check Poetry
if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "Poetry not found!" -ForegroundColor Red
    exit 1
}

# Check Node
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js not found!" -ForegroundColor Red
    exit 1
}

$projectRoot = "c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"
$frontendPath = Join-Path $projectRoot "deep_research\frontend"

# Check frontend deps
if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location $frontendPath
    npm install
    Pop-Location
}

# Start Backend
Write-Host "Starting Python API Backend..." -ForegroundColor Cyan
$backendCmd = "Set-Location '$projectRoot'; poetry run python deep_research/api_server.py"
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
