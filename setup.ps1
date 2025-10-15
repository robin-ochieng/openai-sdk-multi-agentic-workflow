# Quick Start Script for OpenAI SDK Agents
# Run this in PowerShell to set up the project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OpenAI SDK Agents - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Poetry is installed
Write-Host "Checking for Poetry installation..." -ForegroundColor Yellow
$poetryInstalled = Get-Command poetry -ErrorAction SilentlyContinue

if (-not $poetryInstalled) {
    Write-Host "Poetry not found. Installing Poetry..." -ForegroundColor Red
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    
    # Add Poetry to PATH for current session
    $env:Path += ";$env:APPDATA\Python\Scripts"
    
    Write-Host "Poetry installed! Please restart your terminal and run this script again." -ForegroundColor Green
    Write-Host "Or manually add Poetry to PATH and continue." -ForegroundColor Yellow
    exit
} else {
    Write-Host "✓ Poetry is installed" -ForegroundColor Green
}

Write-Host ""

# Install dependencies
Write-Host "Installing project dependencies..." -ForegroundColor Yellow
poetry install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check .env file
Write-Host "Checking for .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
    
    # Read and check if API keys are set
    $envContent = Get-Content ".env" -Raw
    
    if ($envContent -match "OPENAI_API_KEY=\s*$" -or $envContent -match "SENDGRID_API_KEY=\s*$") {
        Write-Host ""
        Write-Host "⚠️  WARNING: Your .env file has empty API keys!" -ForegroundColor Red
        Write-Host "Please edit .env file and add your:" -ForegroundColor Yellow
        Write-Host "  - OPENAI_API_KEY" -ForegroundColor Yellow
        Write-Host "  - SENDGRID_API_KEY" -ForegroundColor Yellow
        Write-Host "  - SENDER_EMAIL" -ForegroundColor Yellow
        Write-Host "  - RECIPIENT_EMAIL" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "See SETUP.md for detailed instructions on getting API keys" -ForegroundColor Cyan
    } else {
        Write-Host "✓ API keys appear to be configured" -ForegroundColor Green
    }
} else {
    Write-Host "✗ .env file not found" -ForegroundColor Red
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env file and add your API keys" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your API keys (if not done already)" -ForegroundColor White
Write-Host "2. Run: poetry shell" -ForegroundColor White
Write-Host "3. Run: python openai_sdk_agent.py" -ForegroundColor White
Write-Host ""
Write-Host "For detailed setup instructions, see SETUP.md" -ForegroundColor Cyan
Write-Host ""
