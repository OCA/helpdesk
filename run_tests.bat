@echo off
REM OCA Test Runner voor Windows CMD
echo =========================================
echo   OCA Lokale Test Runner (CMD)
echo =========================================
echo.

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not found
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker daemon not running
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Check module
if not exist "helpdesk_mgmt" (
    echo ERROR: helpdesk_mgmt not found
    exit /b 1
)

echo [OK] Found helpdesk_mgmt
echo.

REM Pull container
echo Pulling OCA CI container...
docker pull ghcr.io/oca/oca-ci/py3.10-odoo19.0:latest
echo.

REM Start PostgreSQL
echo Starting PostgreSQL...
docker run -d --name oca-postgres-test -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=odoo -p 5433:5432 postgres:13 2>nul
if errorlevel 1 docker start oca-postgres-test 2>nul

echo Waiting for PostgreSQL...
timeout /t 5 /nobreak >nul
echo.

REM Get current directory
set WORKSPACE=%CD%

echo Running OCA tests...
echo Workspace: %WORKSPACE%
echo.

REM Run tests
docker run --rm ^
  --link oca-postgres-test:db ^
  -v "%WORKSPACE%:/workspace" ^
  -e PGHOST=db ^
  -e PGPORT=5432 ^
  -e PGUSER=odoo ^
  -e PGPASSWORD=odoo ^
  -e PGDATABASE=odoo ^
  -e OCA_ENABLE_CHECKLOG_ODOO=1 ^
  ghcr.io/oca/oca-ci/py3.10-odoo19.0:latest ^
  bash -c "echo '[options]' > /etc/odoo.cfg && echo 'addons_path=/workspace,/opt/odoo/addons' >> /etc/odoo.cfg && cd /workspace && echo 'Checking licenses...' && manifestoo -d helpdesk_mgmt check-licenses && echo 'Init test DB...' && oca_init_test_database && echo 'Running tests...' && oca_run_tests"

set TEST_EXIT=%ERRORLEVEL%

echo.
echo Cleaning up...
docker stop oca-postgres-test >nul 2>&1

echo.
if %TEST_EXIT%==0 (
    echo [SUCCESS] All tests passed!
) else (
    echo [FAILED] Tests failed with exit code %TEST_EXIT%
)

exit /b %TEST_EXIT%
