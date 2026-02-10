# Levanta DB + backend + frontend (cada uno en su ventana)
$root = $PSScriptRoot

Write-Host "Levantando base de datos..." -ForegroundColor Cyan
docker compose -f "$root\docker-compose.dev.yml" up -d
if ($LASTEXITCODE -ne 0) { exit 1 }
Start-Sleep -Seconds 3

Write-Host "Abriendo backend (ventana nueva)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$root\backend'; if (Test-Path .\.venv\Scripts\Activate.ps1) { .\.venv\Scripts\Activate.ps1 }; `$env:DATABASE_URL='postgresql://lifehub:lifehub_secret@localhost:5432/lifehub'; uvicorn app.main:app --reload --host 0.0.0.0"
)

Write-Host "Abriendo frontend (ventana nueva)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$root\frontend'; npm run dev"
)

Write-Host "Listo. DB en Docker, backend y frontend en ventanas nuevas." -ForegroundColor Green
Write-Host "App: http://localhost:5173" -ForegroundColor Yellow
