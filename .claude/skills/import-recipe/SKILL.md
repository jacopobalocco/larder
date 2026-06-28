---
description: Importa una ricetta da URL navigando la pagina con Chrome, propone i campi e salva nel DB locale
argument-hint: <URL>
user-invocable: true
---

Importa la ricetta all'URL: $ARGUMENTS

## 1. Carica i tool Chrome

Usa ToolSearch per caricare tutti questi tool in una sola chiamata:
`select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__javascript_tool`

## 2. Naviga alla pagina

- Chiama `tabs_context_mcp` con `createIfEmpty: true`
- Crea un nuovo tab con `tabs_create_mcp`
- Naviga a `$ARGUMENTS`
- Fai uno screenshot per confermare il caricamento

## 3. Estrai i dati della ricetta

Leggi il testo della pagina (`get_page_text`) e usa lo screenshot per ricavare:

| Campo | Tipo | Note |
|---|---|---|
| `name` | string | Titolo della ricetta |
| `description` | string\|null | Breve descrizione se presente |
| `category` | string | Uno tra: `primi` `secondi` `contorni` `zuppe` `dolci` `colazione` |
| `time_min` | int\|null | Tempo totale in minuti |
| `servings` | int | Default 4 se non indicato |
| `kcal` | int\|null | Per porzione |
| `protein_g` | int\|null | Proteine per porzione in grammi |
| `carbs_g` | int\|null | Carboidrati per porzione in grammi |
| `fat_g` | int\|null | Grassi per porzione in grammi |
| `fiber_g` | int\|null | Fibre per porzione in grammi |
| `has_meat` | bool | True se contiene carne, pollame o pesce |
| `image_id` | string\|null | URL diretto dell'immagine principale (vedi step 3b e 3c) |
| `tags` | string[] | 2–3 tag (es. "Veloce", "Vegetariano", "Tradizionale") |
| `ingredients` | list | Vedi formato sotto |
| `steps` | string[] | Passi di preparazione in italiano, uno per elemento |

**Step 3b — Estrai l'immagine dal sito originale:**

Usa `javascript_tool` con questo script (ordine di priorità: og:image → lazy-load attrs → naturalWidth):

```js
// 1. og:image è la fonte più affidabile
const og = document.querySelector('meta[property="og:image"]')?.content
  || document.querySelector('meta[name="twitter:image"]')?.content;
if (og) return [{ src: og, w: 9999, h: 9999, alt: 'og:image' }];

// 2. Scansiona tutti gli img, inclusi quelli lazy-loaded
return Array.from(document.querySelectorAll('img'))
  .map(img => ({
    src: img.src
      || img.getAttribute('data-src')
      || img.getAttribute('data-lazy-src')
      || img.getAttribute('data-original')
      || img.getAttribute('data-srcset')?.split(' ')[0]
      || '',
    w: img.naturalWidth || parseInt(img.getAttribute('width') || '0'),
    h: img.naturalHeight || parseInt(img.getAttribute('height') || '0'),
    alt: img.alt || img.getAttribute('title') || ''
  }))
  .filter(img => img.src.startsWith('http') && (img.w > 200 || img.h > 200))
  .sort((a, b) => (b.w * b.h) - (a.w * a.h))
  .slice(0, 5);
```

Scegli la prima URL valida (dimensioni maggiori). Usa quell'URL come valore di `image_id`.

**Step 3c — Fallback immagine se 3b ha restituito lista vuota o nessun risultato:**

Solo se non hai trovato nessuna immagine dal sito, usa `WebSearch` per trovare una foto adatta:
- Query: `"<nome ricetta>" food photography site:unsplash.com OR site:pexels.com`
- Prendi il primo URL immagine diretto (`.jpg` o `.webp`) trovato nei risultati
- Usalo come `image_id`
- Annota con ⚠️ che l'immagine è un fallback, non quella originale del sito

**Formato ingredienti** (ogni elemento):
- `name`: nome in italiano
- `quantity`: valore numerico oppure `null` per "q.b."
- `unit`: unità (es. `"g"`, `"ml"`, `"cucchiai"`, `"spicchi"`) oppure `null`
- `macro_group`: uno tra `Verdure` `Proteine` `Pasta/Riso` `Latticini` `Condimenti` `Spezie` `Altro`

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
   - Usa `WebSearch` per trovare una foto alternativa: `"<nome ricetta>" food photography site:unsplash.com OR site:pexels.com`
   - Prendi il primo URL `.jpg` o `.webp` diretto
   - Chiama `mcp__larder__update_recipe_image` con: `{ recipe_id: <id>, image_url: <url> }`
   - Ricarica larder (F5) e verifica che l'immagine sia ora visibile
   - Se ancora non appare, prova il prossimo risultato di ricerca (fino a 3 tentativi)
5. **Se l'immagine è presente:** ✅ Processo completato

Mostra: `🖼️ Immagine verificata su larder — ricetta pronta!`
