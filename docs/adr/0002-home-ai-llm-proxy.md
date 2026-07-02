# ADR-0002: Proxy LLM esterno tramite servizio home-ai

- **Status**: Accepted
- **Date**: 2026-06-28

## Context

larder ha bisogno di un LLM per distribuire automaticamente le ricette settimanali rispettando i vincoli familiari (frequenza proteine animali, allergie, preferenze nutrizionali). Le opzioni considerate:

- **Algoritmo Python deterministico** — zero latenza, ma non aggiunge conoscenza né flessibilità al ragionamento.
- **Ollama locale** — privacy totale, ma latenza ~5s su Mac mini M2 con modelli capaci; occupa RAM anche idle.
- **Groq cloud** — latenza ~100ms, tier gratuito sufficiente (30 RPM, 1000 RPD), API key gratuita.

Il secondo problema era dove mettere la logica LLM: embedded in larder significherebbe duplicare la API key e il client in ogni futuro progetto consumer.

## Decision

Creiamo un microservizio separato (`home-ai`, repo pubblico `jacopobalocco/home-ai`) che espone un singolo endpoint `POST /complete` accettando `{prompt, json_mode}` e restituendo `{result}`.

- **Domain-agnostic**: home-ai non conosce ricette, piani alimentari o vincoli familiari. Tutta la logica di dominio (costruzione del prompt, parsing della risposta) rimane in larder.
- **Stack**: FastAPI + Groq SDK, Python 3.12, uv, Docker con `restart: unless-stopped`.
- **Porta**: 8766 (larder usa 8765).
- **Rete**: esposto sulla rete Tailscale (`localhost:8766`), raggiungibile da tutti i device di casa.
- **Provider**: Groq con modello `llama-3.3-70b-versatile`. Sostituibile senza toccare i consumer.

## Consequences

- La logica del prompt per l'auto-distribuzione vive in `larder/api/routes/meal_plan_ai.py` e può evolvere senza ridistribuire home-ai.
- Aggiungere un nuovo progetto consumer richiede solo una chiamata HTTP, nessuna dipendenza condivisa.
- Dipendenza da Groq cloud: se il servizio è down o i limiti gratuiti sono esauriti, l'auto-distribuzione non funziona (funzionalità non critica).
- Docker Desktop deve essere attivo sul Mac mini per il container; se non lo fosse, `make dev` avvia il server in locale senza Docker.
