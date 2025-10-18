# Start API Server - Alternative to Gradio for Next.js Frontend
# Run this instead of app.py when using the Next.js frontend

Write-Host "🚀 Starting Deep Research Agent API Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"

Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow

# Check if fastapi and uvicorn are installed
$checkFastAPI = poetry run python -c "import fastapi; import uvicorn; print('ok')" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Installing FastAPI and Uvicorn..." -ForegroundColor Yellow
    poetry add fastapi uvicorn
}

Write-Host "✅ Dependencies ready" -ForegroundColor Green
Write-Host ""

Write-Host "🌐 Starting API server on port 7863..." -ForegroundColor Cyan
Write-Host "📍 API Endpoint: http://localhost:7863" -ForegroundColor White
Write-Host "📍 API Docs: http://localhost:7863/docs" -ForegroundColor White
Write-Host "📍 Health Check: http://localhost:7863/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Set-Location $projectRoot
poetry run python deep_research/api_server.py
