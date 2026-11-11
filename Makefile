.PHONY: up down logs api web db-shell test lint fmt

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

api:
	cd apps/api && uvicorn app.main:app --reload --port 8000

web:
	cd apps/web && npm run dev

db-shell:
	docker compose exec db psql -U medigraph -d medigraph

test:
	cd apps/api && pytest -q

fmt:
	cd apps/api && black app tests
	cd apps/web && npm run format