# ADR-0003: Chiamata diretta a Groq, rimozione del proxy home-ai

- **Status**: Accepted
- **Date**: 2026-07-02

## Context

ADR-0002 aveva introdotto `home-ai`, un microservizio separato per isolare la
API key Groq e il client LLM da larder, in vista di futuri progetti consumer.
Nella pratica quel secondo consumer non si è mai materializzato, e la
dipendenza da un servizio esterno (raggiungibile via rete Tailscale, con
Docker Desktop attivo sul Mac mini) aggiunge un punto di fallimento e un
requisito di setup che rende più difficile per un nuovo contributor far
partire lo stack con un semplice `git clone`.

## Decision

Rimuoviamo la dipendenza da `home-ai` e portiamo la chiamata al provider Groq
direttamente in larder (`api/routes/meal_plan_ai.py`), usando l'SDK ufficiale
(`AsyncGroq`).

- La API key vive in `GROQ_API_KEY` (variabile d'ambiente, mai committata),
  caricata da `.env` via `python-dotenv`.
- Il modello è configurabile via `GROQ_MODEL` (default `llama-3.3-70b-versatile`).
- L'endpoint HTTP `HOME_AI_URL` e il relativo microservizio non sono più
  necessari per far funzionare larder.

## Consequences

- Un contributor può far partire l'intero stack (API + AI) con un solo
  repository, un solo `.env`, senza servizi esterni da clonare o avviare.
- La API key Groq diventa un requisito diretto di larder invece che di un
  proxy condiviso; se in futuro nascesse un secondo consumer, andrà valutato
  se duplicare l'integrazione o riesumare un proxy dedicato.
- Il repo `home-ai` resta pubblicabile in autonomia ma non è più una
  dipendenza di runtime di larder.
