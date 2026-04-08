import os
from urllib.parse import urlparse

from config.settings.base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

_db_url = os.environ.get(
    "DATABASE_URL",
    "postgres://xtudio:xtudio@localhost:5432/xtudio",
)
_parsed = urlparse(_db_url)

if _parsed.scheme == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / _parsed.path.lstrip("/"),  # noqa: F405
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _parsed.path.lstrip("/"),
            "USER": _parsed.username or "xtudio",
            "PASSWORD": _parsed.password or "xtudio",
            "HOST": _parsed.hostname or "localhost",
            "PORT": str(_parsed.port or 5432),
            "CONN_MAX_AGE": 600,
        }
    }

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INTERNAL_IPS = ["127.0.0.1"]
