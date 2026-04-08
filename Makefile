.PHONY: install migrate makemigrations runserver test test-cov lint typecheck clean collectstatic seed

install:
	pip install -r requirements.txt

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

runserver:
	python manage.py runserver

seed:
	python manage.py seed_platform

test:
	pytest tests/

test-cov:
	pytest tests/ --cov=apps --cov-report=term-missing

test-phase2:
	pytest tests/requirements/ -v --cov=apps/requirements --cov-report=term-missing

test-fast:
	pytest tests/ -x --no-cov

lint:
	ruff check apps/ config/ tests/ management/
	ruff format --check apps/ config/ tests/ management/

lint-fix:
	ruff check --fix apps/ config/ tests/ management/
	ruff format apps/ config/ tests/ management/

typecheck:
	mypy apps/ config/

collectstatic:
	python manage.py collectstatic --noinput

shell:
	python manage.py shell

createsuperuser:
	python manage.py createsuperuser

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache

check: lint typecheck test-cov
	@echo "All checks passed."

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# agent-factory commands
workers:
	python manage.py agent_factory_run_workers

workers-health:
	python manage.py agent_factory_health

reset-stuck:
	python manage.py agent_factory_reset_stuck
