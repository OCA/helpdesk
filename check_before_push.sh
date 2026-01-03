#!/bin/bash
# Dit script zou ik moeten draaien VOOR elke push

echo "=== Running pre-commit checks on changed files ==="
git diff --name-only HEAD | grep -E '\.(py|xml)$' > /tmp/changed_files.txt

if [ -s /tmp/changed_files.txt ]; then
    echo "Changed files:"
    cat /tmp/changed_files.txt
    echo ""
    echo "Running pre-commit..."
    pre-commit run --files $(cat /tmp/changed_files.txt | tr '\n' ' ')
else
    echo "No Python or XML files changed"
fi
