# AGENTS.md

Portable, agent-readable instructions for this project. This file is canonical
and vendor-neutral: Codex, OpenCode, and pi read it natively; Claude reads it
through the `CLAUDE.md` symlink. Keep it concise (< 200 lines).

## Project Overview

<!-- TODO: One or two sentences describing what this project does and who uses it. -->
`larder` — greenfield project scaffolded with an agent-ready baseline.

## Build · Test · Lint

Lint/format are configured (ruff, see `pyproject.toml`). Install and test
commands are still TODO until the toolchain and a test suite are chosen.

```bash
# Install dependencies
# TODO: e.g. `uv sync` or `pip install -e .[dev]`

# Build (if applicable)
# TODO: e.g. `uv build`

# Run tests
# TODO: e.g. `pytest -q`

# Lint
ruff check .

# Format
ruff format .
```

## Code Style

<!-- TODO: Point to the formatter/linter config (e.g. ruff in pyproject.toml). -->
- Follow the project formatter; do not hand-format. Run the format command before committing.
- Prefer small, focused modules and clear names over cleverness.

## Project Structure

<!-- TODO: Update as the codebase grows. -->
- `README.md` — human overview, setup, usage.
- `ARCHITECTURE.md` — high-level design and repo layout.
- `pyproject.toml` — project metadata + ruff (lint/format) config.
- `specs/` — task specifications (see `specs/TEMPLATE.md`).
- `docs/` — project docs, agent-execution policy, ADRs (`docs/adr/`).
- `.github/` — CI, issue/PR templates, CODEOWNERS, Dependabot.
- `LICENSE` — project license.

## Network

Il Mac è connesso alla rete **Tailscale**. Hostname: `localhost` · IP Tailscale: `TAILSCALE-IP`.

Il server dell'app gira su porta configurata. Per accedere dall'iPhone (anch'esso su Tailscale come `iphone-locale`):
```
http://localhost:PORT
```

**Avvio corretto (obbligatorio `--host 0.0.0.0`):**
```bash
uv run python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT
```
Senza `--host 0.0.0.0` il server ascolta solo su localhost e non è raggiungibile da Tailscale.

## Famiglia e Piano Alimentare

**Utente:** (vedi AGENTS.local.md)
**Pranzo:** solo, al lavoro — pasti pratici, trasportabili o da riscaldare, porzione singola
**Cena:** con la famiglia:
- **Compagna**
- **Figlia maggiore** (4 anni) — selettiva, fatica con le verdure visibili; meglio nasconderle o presentarle in modo creativo
- **Figlio minore** (2 anni) — mangia di tutto

**Profilo nutrizionale:**
- Profilo fisico: vedi AGENTS.local.md
- Allenamento: ~5 mattine/settimana → fabbisogno calorico elevato, alto bisogno proteico
- Pranzo post-allenamento (o comunque dopo): privilegiare proteine + carboidrati per recupero muscolare
- Target indicativo: target calorico/proteico: vedi AGENTS.local.md

**Obiettivi di salute (da trainee/GOALS.md — aggiornato 2026-06-29):**
- Peso target: vedi AGENTS.local.md
- HRV e obiettivi: vedi AGENTS.local.md
- Sonno: priorità alta — evitare pasti serali pesanti o infiammatori che compromettano HRV e recupero
- Strategia: surplus calorico mirato a ipertrofia, non solo aumento di peso

**Allergie e intolleranze:**
- **Figlio minore (2 anni):** allergico ad anacardi e pistacchi — nessuna ricetta da cena deve contenerli

**Frequenza proteine animali (regola settimanale):**
- Carne (rossa o bianca): max 1 volta/settimana
- Pesce: max 1 volta/settimana
- Formaggio: max 1 volta/settimana
- Uova: max 1 volta/settimana
- I restanti pasti devono essere a base di legumi, cereali, verdure, tofu o altre proteine vegetali

**Principi guida:**
- Cibo sano, prevalentemente mediterraneo
- Preparazione rapida (≤ 30 min per le cene, idealmente)
- Per la figlia maggiore: verdure integrate negli impasti, passate o camuffate (es. polpette, sughi, vellutate)
- Per l'adulto 1: pranzi calorici e proteici per supportare la crescita muscolare
- Varietà proteica: prevalentemente legumi e cereali integrali, con carne/pesce/formaggio/uova 1x/settimana ciascuno
- Porzioni cena: 4 persone (2 adulti + 2 bimbi piccoli ≈ 3 porzioni adulto)

## Ricette — Siti Supportati per l'Import

La skill `import-recipe` usa `recipe-scrapers` come metodo primario (più veloce e accurato). I siti italiani supportati nativamente:

| Sito | URL |
|---|---|
| Giallo Zafferano | `ricette.giallozafferano.it` |
| Cucchiaio d'Argento | `cucchiaio.it` |
| Misya | `misya.info` |
| La Cucina Italiana | `lacucinaitaliana.it` · `lacucinaitaliana.com` |
| Fatto in Casa da Benedetta | `fattoincasadabenedetta.it` |
| Ricetta.it | `ricetta.it` |
| Ricette per Bimby | `ricetteperbimby.it` |

Per siti non in lista la skill fa automaticamente fallback a Chrome (estrazione manuale). In quel caso l'import funziona ugualmente ma è più lento.

## Ricette — Standardizzazione

Tutte le ricette importate devono essere **sempre**:
- Tradotte completamente in **italiano** (titolo, ingredienti, passaggi, descrizione)
- Porzioni espresse in **sistema metrico** (`g`, `ml`, `cucchiai`, `cucchiaini`), **mai** in unità anglosassoni (`oz`, `cup`, `tsp`)
- Se una ricetta originale usa unità anglosassoni, convertire prima di salvare (es. 1 cup = 240 ml, 1 oz = 28 g)

## Ricette — Immagini: Regola Assoluta

**È VIETATO salvare una ricetta nel DB senza immagine.** Nessuna eccezione.

### Prima di salvare

1. Estrarre l'URL immagine dalla pagina (og:image via `javascript_tool` o `s.image()` da recipe-scrapers)
2. Verificare che l'URL sia valido: `curl -sI <url>` deve restituire `HTTP 200` e `Content-Type: image/`
3. Se l'URL non è valido o mancante → cercare l'immagine sulla **pagina originale** prima di procedere
4. Solo se la pagina originale non ha immagini → cercare su unsplash.com o pexels.com
5. **Non salvare nel DB finché l'immagine non è verificata**
6. **Scaricare l'immagine localmente** prima del salvataggio — le immagini esterne non caricano in larder (hotlink protection). Usa `curl -sL -A "Mozilla/5.0" -e "https://www.google.com/" "<url>" -o "data/images/TMP.jpg"`, poi rinominala a `data/images/<id>.jpg` dopo aver ottenuto l'ID

### Salvataggio immagine locale (obbligatorio)

Le immagini esterne non caricano in larder (hotlink protection). Dopo aver verificato l'URL con `curl -sI`, scaricala localmente **prima di chiamare il POST /recipes/**:

```bash
curl -sL -A "Mozilla/5.0" -e "https://www.google.com/" "<image_url>" -o "data/images/TEMP_ID.jpg"
```

Poi aggiorna `image_id` nel payload con `/images/<id>.jpg` **dopo** aver ottenuto l'ID dal POST, oppure usa `mcp__larder__update_recipe_image` con il path locale.

### Dopo il salvataggio

1. Aprire larder in Chrome (`http://localhost:PORT`)
2. Verificare che il card della ricetta mostri l'immagine (non il placeholder grigio)
3. **Se l'immagine non appare nel browser:**
   - Controllare che `image_id` nel DB sia `/images/<id>.jpg` (path locale)
   - Verificare che il file esista in `data/images/`
   - Riscaricare con `curl` se necessario e aggiornare con `mcp__larder__update_recipe_image`
4. Non considerare l'import completato finché l'immagine non è visibile nel browser

## Agent Log

**Regola obbligatoria:** scrivi in `agent.log` (root del progetto) ogni operazione significativa eseguita durante la sessione. Scopo: tracciabilità cross-sessione di cosa è stato fatto o non fatto.

**Formato — una riga per operazione, il più sintetico possibile:**
```
YYYY-MM-DD HH:MM | AZIONE | dettaglio
```
Esempi:
```
2026-06-27 10:30 | RECIPE_IMPORT | "Pasta al pesto" da giallozafferano.it → OK
2026-06-27 10:31 | RECIPE_IMPORT | "Tiramisù" da cucchiaio.it → FAIL (timeout)
2026-06-27 10:32 | MEAL_PLAN | 2026-06-30 cena → "Pasta al pesto"
2026-06-27 10:33 | DB_QUERY | list_all_recipes → 0 ricette
```

**Regole per risparmiare token:**
- Niente frasi complete: solo verbo + oggetto + esito.
- Nessuna riga per operazioni di sola lettura banali (list/get senza esito rilevante).
- Scrivi nel log PRIMA di rispondere all'utente, così se la sessione si chiude il log è già aggiornato.
- Usa `Bash(echo "..." >> agent.log)` — una chiamata per riga, mai rileggere il log salvo richiesta esplicita.

## Filosofia Cibi: Poco Processati, Ma Pragmatici

**Linea di confine:** rigore dove la ricetta ha importanza organolettica o nutrizionale; praticità dove il processato è equivalente e non sacrifica qualità.

**RIGOROSO (fatto in casa):**
- Ragù, ragù di lenticchie, soffritti → fondamenta del sapore
- Sughi di pomodoro, pesto → qualità ingredienti è centrale
- Brodi (se usati) → estratto di nutrienti
- Verdure da riscaldare/congelare → preparare in batch

**OK COMPRATO (qualità non degradata):**
- Pane → variabilità minima, qualità stabile se buona panetteria
- Pasta (integrale/legumi) → processo industriale non altera nutrimento
- Riso, cereali, legumi secchi → prodotto grezzo
- Formaggi, ricotta → comprati freschi
- Olio, aceto, spezie → base stabile
- Maionese, senape, conserve → poco impatto finale
- Verdure surgelate (se stagione non copre) → nutrienti preservati
- Tofu, tempeh → processato ma proteina pulita

**PRINCIPIO:** Il tempo guadagnato su 30min ricette va a vantaggio della famiglia (meno stress = scelta alimentari migliori). Non è sano stressarsi su surgelati che mantengono nutrienti.

## Safe-to-Run / Security

- Safe-to-run without confirmation: read-only inspection, the test and lint
  commands above, and formatting.
- Ask before: installing/upgrading dependencies, network calls, deleting files,
  pushing, or anything that mutates state outside the working tree.
- Never commit secrets. Secret patterns are covered in `.gitignore`; copy
  `.env.example` to `.env` (gitignored) for local config.
- For the agent execution / sandbox policy, see `docs/agent-execution.md`.
