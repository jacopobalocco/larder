# larder

A personal recipe manager and weekly meal planner, built with FastAPI and a lightweight single-file frontend. Designed for family use with an AI-assisted meal planning feature.

## Features

- **Recipe library** — import recipes from supported Italian cooking sites via URL (powered by `recipe-scrapers`), or add them manually. Each recipe stores ingredients, steps, macros and a local photo.
- **Weekly meal plan** — drag-and-drop calendar UI for assigning recipes to lunch/dinner slots across the week.
- **AI auto-plan** — one-click weekly plan generation via a local AI endpoint, respecting dietary constraints (protein variety limits, allergies, nutritional goals).
- **PDF export** — single-page weekly grid PDF with recipe photos, one column per meal type.
- **Mobile UI** — separate responsive view accessible from any device on the local network.
- **MCP server** — Claude-compatible tool server for agent-driven recipe and meal-plan operations.

## Supported import sites

| Site | URL |
|---|---|
| Giallo Zafferano | `ricette.giallozafferano.it` |
| Cucchiaio d'Argento | `cucchiaio.it` |
| Misya | `misya.info` |
| La Cucina Italiana | `lacucinaitaliana.it` |
| Fatto in Casa da Benedetta | `fattoincasadabenedetta.it` |
| Ricetta.it | `ricetta.it` |
| Ricette per Bimby | `ricetteperbimby.it` |

For unsupported sites the importer falls back to browser-based extraction.

## Stack

- **Backend**: Python 3.12, FastAPI, SQLite, uvicorn
- **Frontend**: Vanilla HTML/JS (no build step)
- **AI**: Groq LLM via the official SDK (`GROQ_API_KEY` env var)
- **Recipe import**: `recipe-scrapers`, with Chrome browser fallback
- **PDF**: `fpdf2` + Pillow
- **Package manager**: `uv`

## Setup

```bash
# Install dependencies
uv sync

# Copy local config and fill in values
cp .env.example .env

# Start the server (use --host 0.0.0.0 to expose on the local network)
uv run python -m uvicorn api.main:app --host 0.0.0.0 --port 8765
```

Open `http://localhost:8765` in your browser.

### MCP server (Claude integration)

```bash
uv run python mcp_server/server.py
```

## Configuration

| Env var | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — (required for AI features) | API key for the Groq LLM, used by meal plan auto-generation |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model used for meal plan auto-generation |

## Development

```bash
ruff check .    # lint
ruff format .   # format
```

See [`AGENTS.md`](AGENTS.md) for agent/contributor instructions and [`docs/`](docs/) for architecture notes and ADRs.

## License

Proprietary — see [`LICENSE`](LICENSE). Contributors retain no commercial rights; see the inline CLA.
