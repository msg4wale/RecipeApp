#!/usr/bin/env python3
"""
Verification script for BE-003 QA validation.
Runs all required tests and connectivity checks.
"""
import subprocess
import sys
import os
import json
from pathlib import Path

# Change to backend directory
backend_dir = Path(__file__).parent / "backend"
os.chdir(backend_dir)

print("="*80)
print("BE-003 VERIFICATION SCRIPT")
print("="*80)
print()

# Step 1: Mailpit connectivity checks
print("STEP 1: MAILPIT CONNECTIVITY CHECKS")
print("-" * 80)

# HTTP API check
print("\n1A. HTTP GET to Mailpit API (http://127.0.0.1:8025/api/v1/info):")
try:
    result = subprocess.run(
        ["curl", "-s", "-i", "http://127.0.0.1:8025/api/v1/info"],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    print("Exit code:", result.returncode)
except Exception as e:
    print(f"ERROR: {e}")

print()

# TCP check
print("1B. TCP Connection Check (localhost:1025):")
try:
    result = subprocess.run(
        ["nc", "-zv", "localhost", "1025"],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    print("Exit code:", result.returncode)
except Exception as e:
    print(f"ERROR: {e}")

print()
print("="*80)
print("STEP 2: PYTEST COLLECTION AND EXECUTION")
print("-" * 80)

# Step 2A: Collect-only for test_admin_chef_verification.py
print("\n2A. Collect-only test_admin_chef_verification.py:")
print("Command: ../.venv/bin/python -m pytest --collect-only -q tests/test_admin_chef_verification.py")
result = subprocess.run(
    ["../.venv/bin/python", "-m", "pytest", "--collect-only", "-q", "tests/test_admin_chef_verification.py"],
    capture_output=True,
    text=True,
    timeout=30
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Exit code:", result.returncode)

print()

# Step 2B: Run focused test suite
print("2B. Run focused test suite:")
print("Command: PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python -m pytest tests/test_admin_chef_verification.py tests/test_chef_onboarding.py tests/test_db_schema.py -q -p no:cacheprovider")
env = os.environ.copy()
env["PYTHONDONTWRITEBYTECODE"] = "1"
result = subprocess.run(
    ["../.venv/bin/python", "-m", "pytest", 
     "tests/test_admin_chef_verification.py",
     "tests/test_chef_onboarding.py", 
     "tests/test_db_schema.py",
     "-q", "-p", "no:cacheprovider"],
    capture_output=True,
    text=True,
    timeout=120,
    env=env
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Exit code:", result.returncode)

print()

# Step 2C: Collect-only for test_email.py to find Mailpit test
print("2C. Collect-only test_email.py (find Mailpit test node IDs):")
print("Command: ../.venv/bin/python -m pytest --collect-only -q tests/test_email.py")
result = subprocess.run(
    ["../.venv/bin/python", "-m", "pytest", "--collect-only", "-q", "tests/test_email.py"],
    capture_output=True,
    text=True,
    timeout=30
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Exit code:", result.returncode)

mailpit_test_node = "tests/test_email.py::test_mailpit_inbox_receives_transactional_email"

print()

# Step 2D: Run Mailpit integration test
print("2D. Run Mailpit integration test:")
print(f"Command: RUN_MAILPIT_INTEGRATION=1 ../.venv/bin/python -m pytest {mailpit_test_node} -v")
env = os.environ.copy()
env["RUN_MAILPIT_INTEGRATION"] = "1"
result = subprocess.run(
    ["../.venv/bin/python", "-m", "pytest", mailpit_test_node, "-v"],
    capture_output=True,
    text=True,
    timeout=30,
    env=env
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Exit code:", result.returncode)

print()
print("="*80)
print("VERIFICATION COMPLETE")
print("="*80)
