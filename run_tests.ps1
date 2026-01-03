# OCA Test Runner voor Windows - Clean version zonder emojis
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  OCA Test Runner - Docker" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker not found" -ForegroundColor Red
    exit 1
}

try {
    docker info | Out-Null
    Write-Host "OK: Docker is running" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker daemon not active" -ForegroundColor Red
    exit 1
}

# Check module
if (!(Test-Path "helpdesk_mgmt")) {
    Write-Host "ERROR: helpdesk_mgmt not found" -ForegroundColor Red
    exit 1
}

Write-Host "OK: Found helpdesk_mgmt module" -ForegroundColor Green
Write-Host ""

# Path conversion
$currentDir = $PWD.Path
$dockerPath = $currentDir -replace '\\', '/' -replace 'C:', '/c'
Write-Host "Workspace: $dockerPath" -ForegroundColor Yellow
Write-Host ""

# Pull container
Write-Host "Pulling OCA CI container..." -ForegroundColor Cyan
docker pull ghcr.io/oca/oca-ci/py3.10-odoo19.0:latest
Write-Host ""

# Start PostgreSQL
Write-Host "Starting PostgreSQL..." -ForegroundColor Cyan
docker run -d --name oca-postgres-test -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=odoo -p 5433:5432 postgres:13 2>$null
if ($LASTEXITCODE -ne 0) { docker start oca-postgres-test 2>$null }

Write-Host "Waiting for PostgreSQL..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host ""

# Run tests
Write-Host "Running OCA tests (this may take 10-15 minutes)..." -ForegroundColor Cyan
Write-Host ""

docker run --rm --link oca-postgres-test:db -v "${dockerPath}:/workspace" -w /workspace -e PGHOST=db -e PGPORT=5432 -e PGUSER=odoo -e PGPASSWORD=odoo -e PGDATABASE=odoo -e OCA_ENABLE_CHECKLOG_ODOO=1 ghcr.io/oca/oca-ci/py3.10-odoo19.0:latest bash -c "ls -la /workspace && echo '' && echo '=== Checking licenses ===' && manifestoo -d /workspace/helpdesk_mgmt check-licenses && echo '' && echo '=== Initializing test database ===' && oca_init_test_database /workspace/helpdesk_mgmt && echo '' && echo '=== Running tests ===' && oca_run_tests /workspace/helpdesk_mgmt"

$exitCode = $LASTEXITCODE

# Cleanup
Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Cyan
docker stop oca-postgres-test 2>$null | Out-Null

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "SUCCESS: All tests passed!" -ForegroundColor Green
} else {
    Write-Host "FAILED: Tests failed with exit code $exitCode" -ForegroundColor Red
}

exit $exitCode
