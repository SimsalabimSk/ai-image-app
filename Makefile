.PHONY: dev up down migrate seed smoke clean

dev: up migrate seed smoke

up:
	docker compose -f infra/docker-compose.yml up -d --build

down:
	docker compose -f infra/docker-compose.yml down -v

migrate:
	docker compose -f infra/docker-compose.yml exec api alembic upgrade head

seed:
	docker compose -f infra/docker-compose.yml exec api python scripts/seed.py

smoke:
	BASE_URL=http://localhost:8000 python scripts/smoke_e2e.py

clean: down
	docker system prune -f
