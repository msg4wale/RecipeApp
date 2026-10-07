#!/bin/bash
set +e

# Command 1
echo "=== COMMAND 1 ==="
echo "COMMAND: curl -s -i http://127.0.0.1:8025/api/v1/info"
OUTPUT=$(curl -s -i http://127.0.0.1:8025/api/v1/info 2>&1)
EXIT_CODE=$?
echo "EXIT CODE: $EXIT_CODE"
echo "STDOUT:"
echo "$OUTPUT"
echo "STDERR: (see output above)"
echo ""

# Command 2
echo "=== COMMAND 2 ==="
echo "COMMAND: nc -zv localhost 1025"
OUTPUT=$(nc -zv localhost 1025 2>&1)
EXIT_CODE=$?
echo "EXIT CODE: $EXIT_CODE"
echo "STDOUT:"
echo "$OUTPUT"
echo "STDERR: (see output above)"
echo ""

# Command 3
echo "=== COMMAND 3 ==="
echo "COMMAND: ../.venv/bin/python -m pytest --collect-only -q tests/test_admin_chef_verification.py"
OUTPUT=$(../.venv/bin/python -m pytest --collect-only -q tests/test_admin_chef_verification.py 2>&1)
EXIT_CODE=$?
echo "EXIT CODE: $EXIT_CODE"
echo "STDOUT:"
echo "$OUTPUT"
echo ""

# Command 4
echo "=== COMMAND 4 ==="
echo "COMMAND: PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python -m pytest tests/test_admin_chef_verification.py tests/test_chef_onboarding.py tests/test_db_schema.py -q -p no:cacheprovider"
OUTPUT=$(PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python -m pytest tests/test_admin_chef_verification.py tests/test_chef_onboarding.py tests/test_db_schema.py -q -p no:cacheprovider 2>&1)
EXIT_CODE=$?
echo "EXIT CODE: $EXIT_CODE"
echo "STDOUT:"
echo "$OUTPUT"
echo ""

# Command 5
echo "=== COMMAND 5 ==="
echo "COMMAND: ../.venv/bin/python -m pytest --collect-only -q tests/test_email.py 2>&1 | grep 'test_mailpit\|test_email'"
OUTPUT=$(../.venv/bin/python -m pytest --collect-only -q tests/test_email.py 2>&1 | grep "test_mailpit\|test_email")
EXIT_CODE=$?
echo "EXIT CODE: $EXIT_CODE"
echo "STDOUT:"
echo "$OUTPUT"
echo ""

# Command 6
echo "=== COMMAND 6 ==="
echo "COMMAND: RUN_MAILPIT_INTEGRATION=1 ../.venv/bin/python -m pytest tests/test_email.py::test_mailpit_inbox_receives_transactional_email -v 2>&1"
OUTPUT=$(RUN_MAILPIT_INTEGRATION=1 ../.venv/bin/python -m pytest tests/test_email.py::test_mailpit_inbox_receives_transactional_email -v 2>&1)
EXIT_CODE=$?
echo "EXIT CODE: $EXIT_CODE"
echo "STDOUT:"
echo "$OUTPUT"
