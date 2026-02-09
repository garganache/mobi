.PHONY: help test-backend test-frontend test-frontend-e2e test-all

help:
	@echo "Available targets:"
	@echo "  make test-backend       # Run backend pytest suite"
	@echo "  make test-frontend      # Run frontend unit tests (Vitest)"
	@echo "  make test-frontend-e2e  # Run frontend E2E tests (Playwright)"
	@echo "  make test-all           # Run backend + frontend (unit + E2E)"

# Backend tests (assumes python3 is installed)

test-backend:
	cd backend && python3 -m venv .venv && \
		. .venv/bin/activate && \
		pip install -r requirements.txt >/dev/null && \
		PYTHONPATH=. pytest

# Frontend unit tests (Vitest)

test-frontend:
	cd frontend && npm install >/dev/null && npm test -- --run

# Frontend E2E tests (Playwright) against local dev servers
# Requires: backend running on :8000 and frontend dev/preview on :5173 or E2E_BASE_URL set

test-frontend-e2e:
	cd frontend && npm install >/dev/null && \
		npx playwright install --with-deps >/dev/null && \
		E2E_BASE_URL=$${E2E_BASE_URL:-http://localhost:5173} npm run test:e2e

# Run everything (backend + frontend unit + E2E)

test-all: test-backend test-frontend
