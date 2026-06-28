---
description: Importa una ricetta da URL usando recipe-scrapers (con fallback Chrome), propone i campi e salva nel DB locale
argument-hint: <URL>
user-invocable: true
---

Importa la ricetta all'URL: $ARGUMENTS

## 1. Estrai con recipe-scrapers (via Bash)

Esegui questo comando:

```bash
uv run python scripts/scrape_recipe.py '$ARGUMENTS'
```

- **Se il JSON non contiene `error`** → usa i dati estratti, vai al passo 3.
- **Se contiene `error`** (sito non supportato, 403, timeout) → vai al passo 2 (fallback Chrome).

## 2. Fallback Chrome (solo se recipe-scrapers fallisce)

Carica i tool Chrome con ToolSearch in una sola chiamata:
`select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__javascript_tool`

- Chiama `tabs_context_mcp` con `createIfEmpty: true`
- Crea un nuovo tab con `tabs_create_mcp`
- Naviga a `$ARGUMENTS` e fai uno screenshot per confermare il caricamento
- Leggi il testo della pagina con `get_page_text` ed estrai manualmente i campi

## 3. Verifica e download immagine PRIMA di procedere (BLOCCO)

**Regola assoluta: non salvare nel DB senza immagine verificata e scaricata localmente.**

Le immagini esterne NON caricano in larder (hotlink protection dai siti sorgente). L'immagine va sempre scaricata localmente.

Dall'output dello scraping hai il campo `image`. Se è null o vuoto:
- Apri la pagina originale in Chrome e usa `javascript_tool` per estrarre og:image
- Se la pagina non ha immagini → cerca su unsplash.com o pexels.com
- **Non procedere al passo 4 finché non hai un URL immagine valido**

Verifica che l'URL sia raggiungibile:
```bash
curl -sI "<image_url>" | grep -E "HTTP|Content-Type"
```
Deve restituire `HTTP 200` e `Content-Type: image/`. Se non passa → trova un altro URL.

Scarica l'immagine localmente (usa un ID temporaneo, poi rinominala dopo il salvataggio):
```bash
curl -sL -A "Mozilla/5.0" -e "https://www.google.com/" "<image_url>" -o "data/images/TMP.jpg"
```
Dopo aver salvato la ricetta e ottenuto l'`id`, rinomina il file e aggiorna il DB:
```bash
mv data/images/TMP.jpg data/images/<id>.jpg
```
Poi chiama `mcp__larder__update_recipe_image` con `image_id = "/images/<id>.jpg"`.

## 4. Compila i campi ricetta

Dai dati estratti (recipe-scrapers o Chrome), ricava:

| Campo | Come ottenerlo |
|---|---|
| `name` | `name` da scrapers, tradotto in italiano se necessario |
| `description` | Breve descrizione se presente nella pagina, altrimenti `null` |
| `category` | Uno tra: `primi` `secondi` `contorni` `zuppe` `dolci` `colazione` |
| `time_min` | `time_min` da scrapers |
| `servings` | Numero da `servings_raw` (es. "4 servings" → 4). Default 4 |
| `kcal` | Da `nutrients` se disponibile, altrimenti `null` |
| `protein_g` | Da `nutrients` se disponibile, altrimenti `null` |
| `carbs_g` | Da `nutrients` se disponibile, altrimenti `null` |
| `fat_g` | Da `nutrients` se disponibile, altrimenti `null` |
| `fiber_g` | Da `nutrients` se disponibile, altrimenti `null` |
| `has_meat` | `true` se ingredienti contengono carne, pollame o pesce |
| `image_id` | `image` da scrapers (URL diretto). Se null → vedi step 3b |
| `tags` | 2–3 tag (es. "Veloce", "Vegetariano", "Tradizionale") |
| `ingredients` | Lista strutturata (vedi formato sotto) |
| `steps` | Lista di passi da `steps`, tradotti in italiano se necessario |

**Formato ingredienti** — ogni elemento da `ingredients` (stringhe grezze come "Petto di pollo 300 g") va convertito in:
- `name`: nome in italiano
- `quantity`: valore numerico oppure `null` per "q.b."
- `unit`: unità (`"g"`, `"ml"`, `"cucchiai"`, `"spicchi"`) oppure `null`
- `macro_group`: uno tra `Verdure` `Proteine` `Pasta/Riso` `Latticini` `Condimenti` `Spezie` `Altro`

**Step 3b — Immagine mancante:** Se `image` è null, usa `javascript_tool` nella tab Chrome già aperta:

```js
const og = document.querySelector('meta[property="og:image"]')?.content
  || document.querySelector('meta[name="twitter:image"]')?.content;
if (og) return og;
return Array.from(document.querySelectorAll('img'))
  .map(img => ({ src: img.src || img.getAttribute('data-src') || '', w: img.naturalWidth, h: img.naturalHeight }))
  .filter(i => i.src.startsWith('http') && (i.w > 200 || i.h > 200))
  .sort((a,b) => (b.w*b.h)-(a.w*a.h))[0]?.src || null;
```

## 4. Proponi i dati estratti

Mostra all'utente un riepilogo leggibile di tutti i campi. Evidenzia con ⚠️ i campi rimasti `null` o stimati.

Chiedi: **"Vuoi salvare questa ricetta? Rispondi `sì` oppure indica le correzioni (es. `porzioni: 6`, `categoria: secondi`)."**

## 5. Applica correzioni ed eventuali modifiche, poi salva

Applica le eventuali correzioni richieste dall'utente al payload, poi chiama:

```
POST http://localhost:PORT/recipes/
Content-Type: application/json

{ ...payload RecipeCreate }
```

In caso di successo mostra: `✅ Ricetta salvata — ID <id>: <name>`.
In caso di errore mostra il messaggio del server e suggerisci cosa correggere.

## 6. Verifica immagine nel browser (OBBLIGATORIO — l'import non è completato senza questo step)

1. **Naviga a larder** (`http://localhost:PORT`) via Chrome
2. **Trova il card** della ricetta appena salvata
3. **L'immagine deve essere visibile** — non il placeholder grigio con il nome
4. **Se il placeholder è ancora visibile:**
   - Ricarica la pagina (F5) e attendi il caricamento completo
   - Se persiste: controlla l'URL immagine nel DB con `mcp__larder__get_recipe`
   - Torna alla pagina originale della ricetta → riestraci og:image con `javascript_tool`
   - Aggiorna con `mcp__larder__update_recipe_image`, ricarica, verifica
   - Ripeti fino a 3 tentativi con URL diversi
   - Solo se la pagina originale è priva di immagini → usa unsplash.com o pexels.com
5. **Solo quando l'immagine è visibile nel browser:** ✅ Import completato

**Non dichiarare mai l'import completato se il card mostra il placeholder.**
