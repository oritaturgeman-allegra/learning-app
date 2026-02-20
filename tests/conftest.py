"""
Shared pytest fixtures for all tests.
"""

import os
import tempfile

# CRITICAL: Set test database BEFORE any backend imports to prevent
# the production database from being used or modified during tests
_test_db_file = tempfile.NamedTemporaryFile(suffix="_test.db", delete=False)
_test_db_path = _test_db_file.name
_test_db_file.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db_path}"
os.environ["TESTING"] = "true"
os.environ["SENTRY_DSN"] = ""  # Disable Sentry during tests
