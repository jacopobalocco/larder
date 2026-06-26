UV := $(HOME)/.local/bin/uv
PYTHON := $(UV) run python

.PHONY: install seed api mcp dev docker-up docker-down help

help:
	@echo "Comandi disponibili:"
	@echo "  make install     - Installa le dipendenze con uv"
	@echo "  make seed        - Popola il DB con ricette di esempio"
	@echo "  make api         - Avvia il backend FastAPI (porta 8000)"
	@echo "  make mcp         - Avvia il server MCP"
	@echo "  make dev         - Seed + API in background + MCP"
	@echo "  make docker-up   - Avvia lo stack con Docker Compose"
	@echo "  make docker-down - Ferma Docker Compose"

install:
	$(UV) sync

seed:
	$(PYTHON) scripts/seed.py

api:
	$(UV) run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

mcp:
	$(PYTHON) mcp_server/server.py

dev: seed
	$(UV) run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
	@echo "API avviata su http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
