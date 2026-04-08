# xtudio — Phase 1: Foundation

## What This Phase Delivers
A fully working Django web application for user management, project creation, and requirements
document upload. No AI agents — this is the foundation everything else is built on.

---

## Features
- ✅ User registration (email-based)
- ✅ User login / logout
- ✅ Google OAuth login
- ✅ User profile management (bio, avatar)
- ✅ Password change and reset (email)
- ✅ Project CRUD (create, edit, archive)
- ✅ Per-user isolated workspace filesystem (auto-created on registration)
- ✅ Document upload: PDF, DOCX, DOC, TXT, MD — max 10MB each
- ✅ Document view (inline in browser) and download
- ✅ Dashboard with project stats
- ✅ Dark theme UI — DM Sans + DM Mono, custom CSS (no Bootstrap)
- ✅ All 5 library apps installed and integrated (audit_trail, notification_hub, pipeline_stages, memory_context, agent_factory)

---

## Tech Stack
- Python 3.11+ / Django 5.1
- PostgreSQL 15+
- django-allauth (email + Google OAuth)
- Custom dark CSS design system

---

## Requirements
- Python 3.11+
- PostgreSQL 15+ (or use Docker)
- Node/npm not required

---

## Local Setup

### 1. Clone and switch to this branch
```bash
git clone <your-repo-url> xtudio
cd xtudio
git checkout phase-1
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start PostgreSQL (Docker)
```bash
docker-compose up -d
```
Or configure your own PostgreSQL and set DATABASE_URL in .env.

### 5. Configure environment
```bash
cp .env.example .env
# Edit .env — set at minimum:
# SECRET_KEY, DATABASE_URL
# Optional: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET (for OAuth)
# Optional: email settings (for password reset)
```

### 6. Run migrations
```bash
python manage.py migrate
```

### 7. Create a superuser (optional)
```bash
python manage.py createsuperuser
```

### 8. Run the development server
```bash
python manage.py runserver
```

Visit: http://localhost:8000

---

## Environment Variables (.env)

```bash
# Required
DJANGO_SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://xtudio:xtudio@localhost:5432/xtudio
DJANGO_SETTINGS_MODULE=config.settings.development

# Optional — Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Optional — Email (for password reset)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@xtudio.dev
```

---

## Make Commands
```bash
make test          # Run test suite
make test-cov      # Run tests with coverage report
make lint          # ruff check — zero errors required
make typecheck     # mypy — zero errors required
make migrate       # Run pending migrations
make lint-fix      # Auto-fix ruff errors where possible
```

---

## Running Tests
```bash
make test-cov
# Expected: 85%+ coverage, zero failures
```

Test settings use SQLite in-memory — no PostgreSQL needed for tests.

---

## Project Structure
```
apps/
├── accounts/        — User model, email auth, Google OAuth
├── workspace/       — WorkspaceService (filesystem abstraction)
├── projects/        — Project CRUD, document upload endpoint
├── documents/       — Document model, view/download
├── dashboard/       — Stats dashboard
│
├── audit_trail/     — Immutable audit log (library app)
├── notification_hub/— In-app notifications (library app)
├── pipeline_stages/ — Hard gates + approval (library app, not yet activated)
├── memory_context/  — 3-tier memory (library app, not yet used)
└── agent_factory/   — Agent orchestration (library app, workers off)
```

---

## Acceptance Criteria — All Met ✅
- [x] User can register, verify email, login, logout
- [x] Google OAuth redirects correctly
- [x] User workspace created automatically on registration
- [x] Project workspace (docs/ + src/) created on project creation
- [x] User can upload PDF, DOCX, TXT, MD files
- [x] Invalid file types rejected with error message
- [x] Files over 10MB rejected with error message
- [x] Documents table shows all project files
- [x] View opens file inline in browser (FileResponse)
- [x] Download saves file as attachment
- [x] All pages use correct dark theme (no Bootstrap)
- [x] `make test-cov` passes — 85%+ coverage
- [x] `make lint` passes — zero ruff errors
- [x] `make typecheck` passes — zero mypy errors

---

## What's NOT in Phase 1
- No AI agents or LLM calls
- No requirements processing or extraction
- No sprint planning or code generation
- No architecture generation

These are added in Phase 2 and beyond. See `README.md` for the full phase list.

---

## Next Phase
**Phase 2 — Requirements Intelligence** (`phase-2` branch)
Adds AI-powered extraction of structured requirements from uploaded documents.
