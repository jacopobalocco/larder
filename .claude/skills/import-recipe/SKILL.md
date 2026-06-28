---
description: Importa una ricetta da URL usando recipe-scrapers (con fallback Chrome), propone i campi e salva nel DB locale
argument-hint: <URL>
user-invocable: true
---

Importa la ricetta all'URL: $ARGUMENTS

## 1. Estrai con recipe-scrapers (via Bash)

Esegui questo comando:

```bash
uv run python -c "
import json, urllib.request
from recipe_scrapers import scrape_html

url = '$ARGUMENTS'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
try:
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    s = scrape_html(html, org_url=url)
    data = {
        'name': s.title(),
        'time_min': s.total_time() or None,
        'servings_raw': s.yields(),
        'image': s.image(),
        'ingredients': s.ingredients(),
        'steps': s.instructions_list(),
    }
    try: data['nutrients'] = s.nutrients()
    except: data['nutrients'] = {}
    print(json.dumps(data, ensure_ascii=False))
except Exception as e:
    print(json.dumps({'error': str(e)}))
"
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

## 3. Compila i campi ricetta

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

## 6. Verifica immagine su larder (CRITICO)

Dopo il salvataggio:

1. **Naviga a larder** (`http://localhost:PORT`) via Chrome
2. **Scorri finché non trovi** la ricetta appena salvata nella lista
3. **Controlla se l'immagine è visibile** nel card della ricetta
4. **Se l'immagine manca:**
   - Controlla l'URL salvato nel DB — deve iniziare con `http`
   - Se l'URL è rotto: torna alla pagina originale della ricetta e riestraci l'immagine (non usare Unsplash se il sito originale ha un'immagine)
   - Chiama `mcp__larder__update_recipe_image` con il nuovo URL
   - Ricarica larder (F5) e verifica — fino a 3 tentativi
5. **Se l'immagine è presente:** ✅ Processo completato

Mostra: `🖼️ Immagine verificata su larder — ricetta pronta!`
