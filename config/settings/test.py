# Claude Code: implement test settings
# Extends base.py
# Key requirements:
# - SQLite in-memory database (NOT PostgreSQL)
# - EMAIL_BACKEND = locmem
# - AGENT_FACTORY_AUTO_START_WORKERS = False
# - WORKSPACE_ROOT = tempfile.mkdtemp()
# - PASSWORD_HASHERS with fast hasher for tests

from pathlib import Path

from config.settings.base import *  # noqa: F401, F403

# SQLite in-memory for tests — fast, no PostgreSQL needed
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

AGENT_FACTORY_AUTO_START_WORKERS = False

# Fast password hasher for tests
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Temp workspace for tests
import tempfile  # noqa: E402

WORKSPACE_ROOT = Path(tempfile.mkdtemp())
