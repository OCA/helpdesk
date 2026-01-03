#!/bin/bash
# Script om OCA tests lokaal te draaien zoals GitHub Actions dat doet

echo "=== OCA Lokale Test Runner ==="
echo ""
echo "Deze script simuleert de GitHub Actions test workflow."
echo "Het gebruikt dezelfde Docker containers als de CI."
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is niet geïnstalleerd of niet in PATH"
    echo ""
    echo "Installeer Docker Desktop voor Windows:"
    echo "https://docs.docker.com/desktop/install/windows-install/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is niet actief"
    echo "Start Docker Desktop"
    exit 1
fi

echo "✅ Docker is beschikbaar"
echo ""

# Use the same container as GitHub Actions
CONTAINER="ghcr.io/oca/oca-ci/py3.10-odoo19.0:latest"
echo "��� Pulling OCA CI container..."
docker pull $CONTAINER

# Create a PostgreSQL container if not exists
echo "���️  Starting PostgreSQL..."
docker run -d --name oca-postgres-test \
    -e POSTGRES_USER=odoo \
    -e POSTGRES_PASSWORD=odoo \
    -e POSTGRES_DB=odoo \
    -p 5433:5432 \
    postgres:13 2>/dev/null || docker start oca-postgres-test

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
sleep 5

# Run tests in the OCA container
echo "��� Running tests..."
echo ""

# Get the addon name from the first module directory found
ADDON_NAME=$(ls -d helpdesk_mgmt 2>/dev/null | head -1)

if [ -z "$ADDON_NAME" ]; then
    echo "❌ Geen helpdesk_mgmt module gevonden in $(pwd)"
    exit 1
fi

echo "📦 Testing module: $ADDON_NAME"
echo ""

# Convert Windows path to Unix path for Docker
WORKSPACE_PATH=$(pwd -W 2>/dev/null || pwd)
WORKSPACE_PATH=${WORKSPACE_PATH//\\/\/}  # Convert backslashes to forward slashes
WORKSPACE_PATH=${WORKSPACE_PATH//:/}     # Remove drive letter colon
WORKSPACE_PATH="/${WORKSPACE_PATH}"      # Add leading slash

echo "🔍 Workspace path: $WORKSPACE_PATH"
echo ""

docker run --rm \
    --link oca-postgres-test:db \
    -v "$WORKSPACE_PATH:/workspace" \
    -w /workspace \
    -e PGHOST=db \
    -e PGPORT=5432 \
    -e PGUSER=odoo \
    -e PGPASSWORD=odoo \
    -e PGDATABASE=odoo \
    -e OCA_ENABLE_CHECKLOG_ODOO=1 \
    $CONTAINER \
    bash -c "
        ls -la /workspace && \
        echo '' && \
        echo '=== Checking licenses ===' && \
        manifestoo -d /workspace/$ADDON_NAME check-licenses || echo 'Skipping license check' && \
        echo '' && \
        echo '=== Initializing test database ===' && \
        oca_init_test_database /workspace/$ADDON_NAME && \
        echo '' && \
        echo '=== Running tests ===' && \
        oca_run_tests /workspace/$ADDON_NAME
    "

TEST_EXIT_CODE=$?

# Cleanup
echo ""
echo "��� Cleaning up..."
docker stop oca-postgres-test &>/dev/null

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ ALLE TESTS GESLAAGD!"
else
    echo ""
    echo "❌ TESTS GEFAALD (exit code: $TEST_EXIT_CODE)"
fi

exit $TEST_EXIT_CODE
