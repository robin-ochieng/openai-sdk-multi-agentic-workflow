# Deep Research Agent - Next.js Frontend Setup Script

Write-Host "🚀 Setting up Deep Research Agent Next.js Frontend..." -ForegroundColor Cyan
Write-Host ""

# Navigate to frontend directory
Set-Location "deep_research/frontend"

Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install

Write-Host ""
Write-Host "✅ Dependencies installed!" -ForegroundColor Green
Write-Host ""

Write-Host "🔧 Setting up additional packages..." -ForegroundColor Yellow
npm install -D tailwindcss-animate
npm install @hookform/resolvers zod react-hook-form

Write-Host ""
Write-Host "📝 Creating missing package.json scripts..." -ForegroundColor Yellow

Write-Host ""
Write-Host "✨ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Make sure your Python backend is running:"
Write-Host "     poetry run python deep_research/app.py" -ForegroundColor White
Write-Host ""
Write-Host "  2. Start the Next.js development server:"
Write-Host "     npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "  3. Open your browser to:"
Write-Host "     http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Happy researching!" -ForegroundColor Magenta
