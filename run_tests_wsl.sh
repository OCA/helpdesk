#!/bin/bash
# OCA Test Runner via WSL - Meest betrouwbaar voor Windows
# Dit draait in WSL en heeft geen path conversion problemen

echo "========================================="
echo "  OCA Test Runner (via WSL)"
echo "========================================="
echo ""

# Check Docker
if ! docker --version >/dev/null 2>&1; then
    echo "❌ Docker niet gevonden"
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker daemon niet actief"
    exit 1
fi

echo "✅ Docker is actief"
echo ""

# Convert Windows path to WSL path
WINDOWS_PATH="/mnt/c/Users/Sybde/Projects/helpdesk/oca-helpdesk-19"

if [ ! -d "$WINDOWS_PATH/helpdesk_mgmt" ]; then
    echo "❌ helpdesk_mgmt niet gevonden in $WINDOWS_PATH"
    exit 1
fi

echo "✅ Module gevonden: helpdesk_mgmt"
echo ""

# Pull container
echo "Pulling OCA CI container..."
docker pull ghcr.io/oca/oca-ci/py3.10-odoo19.0:latest
echo ""

# Start PostgreSQL
echo "Starting PostgreSQL..."
docker run -d --name oca-postgres-test \
    -e POSTGRES_USER=odoo \
    -e POSTGRES_PASSWORD=odoo \
    -e POSTGRES_DB=odoo \
    -p 5433:5432 \
    postgres:13 2>/dev/null || docker start oca-postgres-test

echo "Waiting for PostgreSQL..."
sleep 5
echo ""

# Run tests
echo "Running OCA tests (10-15 minutes)..."
echo "Workspace: $WINDOWS_PATH"
echo ""

docker run --rm \
    --link oca-postgres-test:db \
    -v "$WINDOWS_PATH:/workspace" \
    -e PGHOST=db \
    -e PGPORT=5432 \
    -e PGUSER=odoo \
    -e PGPASSWORD=odoo \
    -e PGDATABASE=odoo \
    -e OCA_ENABLE_CHECKLOG_ODOO=1 \
    ghcr.io/oca/oca-ci/py3.10-odoo19.0:latest \
    bash -c "
        cd /workspace && \
        echo '=== Module contents ===' && \
        ls -la helpdesk_mgmt | head -20 && \
        echo '' && \
        echo '=== Checking licenses ===' && \
        manifestoo -d helpdesk_mgmt check-licenses && \
        echo '' && \
        echo '=== Initializing test database ===' && \
        oca_init_test_database helpdesk_mgmt && \
        echo '' && \
        echo '=== Running tests ===' && \
        oca_run_tests helpdesk_mgmt
    "

EXIT_CODE=$?

# Cleanup
echo ""
echo "Cleaning up..."
docker stop oca-postgres-test >/dev/null 2>&1

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ SUCCESS: All tests passed!"
else
    echo "❌ FAILED: Tests failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE
