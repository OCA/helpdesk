@echo off
echo ====================================
echo Quick OCA Test - Diagnose Mode
echo ====================================
echo.

REM Start PostgreSQL
echo Starting PostgreSQL...
docker run -d --name oca-postgres-test -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=odoo -p 5433:5432 postgres:13 2>nul
if errorlevel 1 docker start oca-postgres-test 2>nul
timeout /t 3 /nobreak >nul
echo.

REM Quick test - just try to install helpdesk_mgmt
echo Running quick installation test...
echo.

docker run --rm ^
  --link oca-postgres-test:db ^
  -v "%CD%:/workspace" ^
  -e PGHOST=db ^
  -e PGPORT=5432 ^
  -e PGUSER=odoo ^
  -e PGPASSWORD=odoo ^
  -e PGDATABASE=odoo ^
  ghcr.io/oca/oca-ci/py3.10-odoo19.0:latest ^
  bash -c "cd /workspace && echo '=== Module structure ===' && ls -la helpdesk_mgmt && echo '' && echo '=== Checking manifest ===' && python3 -c 'import ast; print(ast.literal_eval(open(\"helpdesk_mgmt/__manifest__.py\").read()))' && echo '' && echo '=== Installing helpdesk_mgmt ===' && oca_init_test_database helpdesk_mgmt 2>&1 | tail -50"

set EXIT_CODE=%ERRORLEVEL%

echo.
echo Cleaning up...
docker stop oca-postgres-test >nul 2>&1

if %EXIT_CODE%==0 (
    echo [SUCCESS] Module can be installed
) else (
    echo [FAILED] Module installation failed - check output above
)

pause
