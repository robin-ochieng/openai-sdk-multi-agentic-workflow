# Start Deep Research Agent API v2.0
# Production-ready API with authentication and rate limiting

Write-Host "Starting Deep Research Agent API v2.0..." -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "deep_research/api/main.py")) {
    Write-Host "Error: Please run this script from the project root (openai-sdk-multi-agentic-workflow)" -ForegroundColor Red
    exit 1
}

# Check for virtual environment
if (Test-Path ".venv") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\.venv\Scripts\Activate.ps1
}

# Check for required packages
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$packages = @("fastapi", "uvicorn", "pydantic-settings", "PyJWT", "supabase")
$missing = @()

foreach ($pkg in $packages) {
    $installed = pip show $pkg 2>$null
    if (-not $installed) {
        $missing += $pkg
    }
}

if ($missing.Count -gt 0) {
    Write-Host "Installing missing packages: $($missing -join ', ')" -ForegroundColor Yellow
    pip install $($missing -join ' ')
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deep Research Agent API v2.0" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Endpoints:" -ForegroundColor Cyan
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Health:    http://localhost:8000/health" -ForegroundColor White
Write-Host "  Auth:      http://localhost:8000/api/auth/*" -ForegroundColor White
Write-Host "  Research:  http://localhost:8000/api/research/*" -ForegroundColor White
Write-Host "  Users:     http://localhost:8000/api/users/*" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the API server
uvicorn deep_research.api.main:app --host 0.0.0.0 --port 8000 --reload
