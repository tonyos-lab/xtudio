# Local Setup Guide

Get xtudio running on your machine in under 10 minutes.

---

## Requirements

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | Check: `python --version` |
| pip | latest | Check: `pip --version` |
| Git | any | Check: `git --version` |
| PostgreSQL **or** Docker | 15+ / any | Only needed if you choose the PostgreSQL path — SQLite works fine locally |

> **SQLite is fully supported for local development.** You do not need PostgreSQL or Docker
> to run xtudio on your machine. Choose the database option that suits you below.

---

## Step 1 — Clone the Repository

```bash
git clone <repo-url> xtudio
cd xtudio
git checkout phase-1
```

> Each phase is an independent, self-contained branch. Start with `phase-1`.

---

## Step 2 — Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Your prompt should show `(.venv)` when the environment is active.

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4 — Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Open `.env` and set the following values.

### Option A — SQLite (quickest, no database server needed)

```bash
DJANGO_SECRET_KEY=any-long-random-string-here
DJANGO_SETTINGS_MODULE=config.settings.development

# SQLite — file created automatically in the project root
DATABASE_URL=sqlite:///db.sqlite3
```

That's all that's required to run locally with SQLite.

---

### Option B — PostgreSQL via Docker

```bash
DJANGO_SECRET_KEY=any-long-random-string-here
DJANGO_SETTINGS_MODULE=config.settings.development

# PostgreSQL — matches docker-compose.yml defaults
DATABASE_URL=postgresql://xtudio:xtudio@localhost:5432/xtudio
```

Start the database container:

```bash
docker-compose up -d
```

---

### Option C — PostgreSQL (existing local install)

```bash
DJANGO_SECRET_KEY=any-long-random-string-here
DJANGO_SETTINGS_MODULE=config.settings.development
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<dbname>
```

Create the database first:

```bash
createdb <dbname>
```

---

### Generating a secret key

Paste this into your terminal to generate a secure key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copy the output into `DJANGO_SECRET_KEY=` in your `.env`.

---

## Step 5 — Run Migrations

```bash
python manage.py migrate
```

---

## Step 6 — (Optional) Create a Superuser

Gives access to the Django admin at `/admin/`:

```bash
python manage.py createsuperuser
```

Follow the prompts. You can also just register via the normal signup page.

---

## Step 7 — Start the Development Server

```bash
python manage.py runserver
```

Open your browser at: **http://localhost:8000**

---

## First Login

1. Go to **http://localhost:8000/accounts/register/**
2. Register with any email and password
3. You'll be redirected to the dashboard automatically

> Login uses **email address**, not a username.

---

## Optional — Google Sign-In

To enable "Continue with Google" on the login and register pages, follow the step-by-step guide:
**[GOOGLE_SIGNIN.md](GOOGLE_SIGNIN.md)**

Google Sign-In is completely optional — email/password registration always works without it.

---

## Useful Make Commands

```bash
make runserver      # Start the development server
make migrate        # Run pending migrations
make test           # Run the test suite
make test-cov       # Run tests with coverage report
make lint           # Check code style (ruff)
make typecheck      # Check types (mypy)
```

See [TESTING.md](TESTING.md) for the full testing guide.

---

## Troubleshooting

**`ModuleNotFoundError` or import errors**
Make sure your virtual environment is activated (`(.venv)` in your prompt) and dependencies are installed.

**`django.db.utils.OperationalError: no such table`**
Run `python manage.py migrate` — migrations haven't been applied yet.

**`DJANGO_SETTINGS_MODULE` not set error**
Ensure `.env` contains `DJANGO_SETTINGS_MODULE=config.settings.development` and that `python-dotenv` loaded it. Alternatively, export it manually:
```bash
export DJANGO_SETTINGS_MODULE=config.settings.development
```

**PostgreSQL connection refused**
If using Docker, check the container is running: `docker-compose ps`. If using a local install, confirm PostgreSQL is started and the `DATABASE_URL` credentials are correct.

**Port 8000 already in use**
Run on a different port: `python manage.py runserver 8080`

**Static files not loading**
Run `python manage.py collectstatic` — only needed in production. In development (`DEBUG=True`) static files are served automatically.