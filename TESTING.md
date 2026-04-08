# Testing Guide

## Overview

xtudio uses **pytest** with **pytest-django**, **factory-boy**, and **pytest-mock**.

Key facts before you start:
- The test database is **SQLite in-memory** — no PostgreSQL required to run tests
- **No `.env` file needed** — test settings are fully self-contained
- Minimum coverage enforced: **85%** (configured in `pyproject.toml`)

---

## Prerequisites

1. Python 3.11+ with a virtual environment activated
2. Dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

That's it. No database server, no `.env`, no external services.

---

## Running the Test Suite

### Using Make (recommended)

| Command | What it does |
|---|---|
| `make test` | Run all tests, no coverage |
| `make test-cov` | Run all tests + coverage report (85% minimum enforced) |
| `make test-fast` | Run tests, stop on first failure, no coverage |
| `make check` | Run lint + typecheck + test-cov all at once |

### Using pytest directly

```bash
# Run all tests
python -m pytest tests/

# Run a single app
python -m pytest tests/projects/ -v

# Run a single file
python -m pytest tests/projects/test_services.py -v

# Run a single test
python -m pytest tests/projects/test_services.py::TestProjectService::test_create_project -v

# With coverage
python -m pytest tests/ --cov=apps --cov-report=term-missing
```

---

## Understanding the Coverage Report

After `make test-cov` you'll see output like:

```
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
apps/projects/services.py        57      8    86%   40-41, 52-53
apps/documents/views.py          50      0   100%
...
TOTAL                           529     40    92%
```

- **Stmts** — total executable lines
- **Miss** — lines not executed by any test
- **Cover** — percentage covered
- **Missing** — exact line numbers not covered

The suite fails if `TOTAL` drops below **85%**. Focus coverage on service methods and view paths — these are the highest priority.

---

## Test Structure

```
tests/
├── conftest.py          — shared fixtures used across all tests
├── factories.py         — factory-boy factories for all models
├── accounts/
│   ├── test_models.py   — User model tests
│   ├── test_signals.py  — workspace auto-creation on registration
│   └── test_views.py    — register, login, logout, profile views
├── dashboard/
│   └── test_views.py    — dashboard stats and context
├── documents/
│   ├── test_models.py   — Document model tests
│   ├── test_services.py — upload, delete, serve file logic
│   └── test_views.py    — view, download, delete views
├── projects/
│   ├── test_models.py   — Project model tests
│   ├── test_services.py — create, update, archive logic
│   └── test_views.py    — list, create, detail, edit, archive, upload views
└── workspace/
    └── test_services.py — WorkspaceService: path safety, file I/O
```

---

## Shared Fixtures

Defined in `tests/conftest.py` and available in every test:

| Fixture | What it provides |
|---|---|
| `user` | A `User` instance created via `UserFactory` |
| `other_user` | A second `User` (useful for ownership/permission checks) |
| `project` | A `Project` owned by `user` |
| `document` | A `Document` belonging to `project` |
| `client` | An unauthenticated Django test client |
| `authenticated_client` | A test client force-logged in as `user` |

### Filesystem tests

Any test that touches the workspace filesystem must redirect it to a temporary directory:

```python
def test_something(db, settings, tmp_path):
    settings.WORKSPACE_ROOT = tmp_path
    # All workspace operations now go to the temp directory
```

---

## Writing New Tests

### Model tests
```python
@pytest.mark.django_db
class TestMyModel:
    def test_str_returns_name(self):
        obj = MyModelFactory(name="Example")
        assert str(obj) == "Example"
```

### Service tests
```python
@pytest.mark.django_db
class TestMyService:
    def test_create_returns_object(self, user, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        result = MyService.create(owner=user, name="Test")
        assert result.pk is not None
        assert result.owner == user
```

### View tests
```python
@pytest.mark.django_db
class TestMyView:
    def test_requires_login(self, client):
        response = client.get("/my-url/")
        assert response.status_code == 302
        assert "login" in response.url

    def test_returns_200_for_owner(self, authenticated_client, project):
        url = reverse("my-view", kwargs={"project_id": project.id})
        response = authenticated_client.get(url)
        assert response.status_code == 200
```

### Adding a factory for a new model

Add to `tests/factories.py`:

```python
class MyModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MyModel

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Item {n}")
```

---

## Rules

1. **No external API calls in tests.** If a service calls an AI agent, mock it:
   ```python
   def test_trigger(mocker, project, user):
       mock = mocker.patch("apps.agent_factory.factory.AgentFactory.run_agent_async")
       mock.return_value = {"job_id": "test-123", "status": "queued"}
       result = MyService.trigger(project=project, user=user)
       mock.assert_called_once()
   ```

2. **Always use `tmp_path` for workspace tests.** Never write to the real `workspace/` directory in tests.

3. **Mark every DB test.** Use `@pytest.mark.django_db` on the class or function. Without it, any database access raises an error.

4. **Coverage must not decrease.** The 85% floor is enforced — new code needs new tests.

---

## Linting and Type Checking

Tests alone are not enough — all three checks must pass before a contribution is merged:

```bash
make lint        # ruff — checks code style and imports (zero errors required)
make typecheck   # mypy — checks type annotations (zero errors required)
make test-cov    # pytest — runs tests with coverage (85%+ required)

make check       # runs all three in sequence
```

---

## Troubleshooting

**`ModuleNotFoundError` on import**
Make sure your virtual environment is activated and `pip install -r requirements.txt` has been run.

**`django.db.utils.OperationalError: no such table`**
This shouldn't happen with in-memory SQLite — pytest-django runs migrations automatically. If it does, check that `DJANGO_SETTINGS_MODULE` is set to `config.settings.test`.

**`PermissionError` or `FileNotFoundError` in workspace tests**
You're missing `settings.WORKSPACE_ROOT = tmp_path` in the test. Add it alongside the `tmp_path` fixture.

**Coverage below 85%**
Run `make test-cov` and look at the `Missing` column. Add tests for the uncovered lines — error paths and edge cases are the most common gaps.
