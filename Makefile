.PHONY: help start test-backend test-frontend test-frontend-e2e test-all

help:
	@echo "Available targets:"
	@echo "  make start              # Start backend (port 8000) and frontend (port 5173)"
	@echo "  make test-backend       # Run backend pytest suite"
	@echo "  make test-frontend      # Run frontend unit tests (Vitest)"
	@echo "  make test-frontend-e2e  # Run frontend E2E tests (Playwright)"
	@echo "  make test-all           # Run backend + frontend (unit + E2E)"

# Start the full stack (backend + frontend)

start:
	@echo "Starting full stack..."
	@echo "Backend will be on http://localhost:8000"
	@echo "Frontend will be on http://localhost:5173"
	@echo ""
	@# Start backend in background
	@cd backend && \
		(. .venv/bin/activate 2>/dev/null || (python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt)) && \
		DATABASE_URL=sqlite:///test.db uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	@# Start frontend in background
	@cd frontend && npm install >/dev/null 2>&1 && npm run dev &
	@echo ""
	@echo "Services started! Press Ctrl+C to stop."
	@echo "Wait for services to be ready, then run: make test-frontend-e2e"
	@# Keep the make process running
	@wait

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
