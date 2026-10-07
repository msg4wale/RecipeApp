# BE-003 Test Verification Guide

## Quick Start
Execute these commands from `/Users/araji/Dev-Workspace/Recipe app/backend/`:

### Mailpit Connectivity Checks
```bash
# HTTP API connectivity check
curl -s -i http://127.0.0.1:8025/api/v1/info

# SMTP TCP port connectivity check
nc -zv localhost 1025
```

### Test Execution

#### 1. Collect test_admin_chef_verification.py test nodes
```bash
../.venv/bin/python -m pytest --collect-only -q tests/test_admin_chef_verification.py
```

**Expected Output:** Should list 8 test collection nodes (7 test functions, 1 parametrized with 2 params)

#### 2. Run focused test suite (main tests)
```bash
PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python -m pytest tests/test_admin_chef_verification.py tests/test_chef_onboarding.py tests/test_db_schema.py -q -p no:cacheprovider
```

**Expected Output:** Summary of passed/failed/skipped tests

#### 3. Find Mailpit integration test node ID
```bash
../.venv/bin/python -m pytest --collect-only -q tests/test_email.py
```

**Expected Output:** Should include `tests/test_email.py::test_mailpit_inbox_receives_transactional_email`

#### 4. Run Mailpit integration test
```bash
cd /Users/araji/Dev-Workspace/Recipe\ app/backend && \
RUN_MAILPIT_INTEGRATION=1 ../.venv/bin/python -m pytest tests/test_email.py::test_mailpit_inbox_receives_transactional_email -v
```

**Expected Behavior:**
- If Mailpit is unavailable: Will skip with message "Mailpit inbox API is unavailable"
- If Mailpit is available: Will send test email and verify it appears in inbox within 10 seconds

---

## Test Suite Breakdown

### test_admin_chef_verification.py (7 tests, 8 nodes due to parametrization)

**ENG-AC-089**: Authorization checks
- `test_admin_queue_requires_admin_and_returns_private_certificate_link`
  - Verifies unauthenticated users get 401
  - Verifies non-Admin users get 403
  - Verifies Admin users get 200 with private certificate URL

**ENG-AC-091/092/097**: Approval and Rejection behavior
- `test_admin_approval_promotes_applicant_and_persists_review_audit`
  - Transitions applicant from regular → chef role
  - Persists reviewer ID, timestamp, and rationale
  - Sends notification
  - Rejects duplicate decisions (409 Conflict)

- `test_admin_rejection_keeps_regular_role_and_persists_review_audit`
  - Keeps applicant as regular role
  - Persists review audit fields
  - Sends rejection notification
  - Rejects duplicate decisions

**ENG-AC-095**: Failure after committed decision
- `test_notification_delivery_failure_is_explicit_after_committed_decision` (parametrized: approve, reject)
  - Accepts decision and updates state even if email fails
  - Returns 503 with explicit error message
  - Persists decision/audit to database
  - Rejects retry (409 Conflict)

**ENG-AC-093**: Invalid requests
- `test_decision_rejects_missing_or_invalid_applications`
  - Missing applications: 404 Not Found
  - Invalid decision values: 422 Unprocessable Entity

**Other critical tests**:
- `test_queue_reports_certificate_storage_failure` - Storage unavailability returns 503
- `test_decision_database_failure_rolls_back_application_and_user` - DB failure doesn't send email/update state

### test_chef_onboarding.py (Multiple tests)
- Email verification token lifecycle
- Token verification and consumption
- Access log security (no token leaking)
- Certificate upload workflow

### test_db_schema.py (2 tests)
- Required tables exist
- Core columns exist (users, sessions, chef_verifications, recipes, etc.)

### test_email.py (Multiple tests + Mailpit integration)
- SMTP sender constructs/delivers messages correctly
- Error handling and retry logic
- **test_mailpit_inbox_receives_transactional_email** - Live integration test

---

## What to Look For in Output

### Success Indicators
```
passed: XX
failed: 0
error: 0
skipped: 0  (or acceptable count for Mailpit test)
```

### Test Names in Output
Should see these in test_admin_chef_verification.py collection:
- test_admin_queue_requires_admin_and_returns_private_certificate_link
- test_admin_approval_promotes_applicant_and_persists_review_audit
- test_admin_rejection_keeps_regular_role_and_persists_review_audit
- test_notification_delivery_failure_is_explicit_after_committed_decision[approve]
- test_notification_delivery_failure_is_explicit_after_committed_decision[reject]
- test_decision_rejects_missing_or_invalid_applications
- test_queue_reports_certificate_storage_failure
- test_decision_database_failure_rolls_back_application_and_user

### Mailpit Test Behavior
```
# If Mailpit is NOT available:
SKIPPED - set RUN_MAILPIT_INTEGRATION=1 to run the Mailpit integration check
# or
SKIPPED - Mailpit inbox API is unavailable

# If Mailpit IS available:
PASSED - Email appeared in inbox within timeout
# or
FAILED - Email did not appear in the Mailpit inbox before the timeout
```

---

## Environment Requirements
- Python venv at `backend/.venv`
- PostgreSQL/SQLite configured (tests use in-memory SQLite by default)
- Mailpit running on `localhost:1025` (SMTP) and `localhost:8025` (HTTP API) for integration test
- pytest and dependencies installed

## Output Capture Instructions
Run each command in sequence and capture:
1. Complete stdout
2. Complete stderr
3. Exit code (echo $?)

Example capture:
```bash
../.venv/bin/python -m pytest --collect-only -q tests/test_admin_chef_verification.py
echo "Exit code: $?"
```

---

## Notes
- Tests use mocked storage and email by default
- In-memory SQLite database for test isolation
- No external services required except optional Mailpit for integration test
- Test execution should complete in under 2 minutes total
- No service lifecycle operations (start/stop) are performed
