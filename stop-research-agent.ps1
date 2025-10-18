# Stop All Servers - Cleanup Script
# This script helps you stop both the Python backend and Next.js frontend

Write-Host "🛑 Stopping Deep Research Agent Servers" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Find and kill Python processes on port 7863
Write-Host "🐍 Stopping Python Backend (port 7863)..." -ForegroundColor Yellow
$pythonProcesses = Get-NetTCPConnection -LocalPort 7863 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

if ($pythonProcesses) {
    foreach ($pid in $pythonProcesses) {
        try {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "  Stopping process: $($process.ProcessName) (PID: $pid)" -ForegroundColor Gray
                Stop-Process -Id $pid -Force
            }
        } catch {
            Write-Host "  Could not stop process PID: $pid" -ForegroundColor Gray
        }
    }
    Write-Host "✅ Python backend stopped" -ForegroundColor Green
} else {
    Write-Host "  No process found on port 7863" -ForegroundColor Gray
}
Write-Host ""

# Find and kill Node.js processes on port 3000
Write-Host "⚡ Stopping Next.js Frontend (port 3000)..." -ForegroundColor Yellow
$nodeProcesses = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

if ($nodeProcesses) {
    foreach ($pid in $nodeProcesses) {
        try {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "  Stopping process: $($process.ProcessName) (PID: $pid)" -ForegroundColor Gray
                Stop-Process -Id $pid -Force
            }
        } catch {
            Write-Host "  Could not stop process PID: $pid" -ForegroundColor Gray
        }
    }
    Write-Host "✅ Next.js frontend stopped" -ForegroundColor Green
} else {
    Write-Host "  No process found on port 3000" -ForegroundColor Gray
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Red
Write-Host "✨ All servers stopped successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
