# Idee e Backlog

Raccolta di funzionalità future, non ancora schedulate.

---

## Export PDF piano settimanale

Generare un PDF scaricabile con le ricette della settimana: titolo, ingredienti, passi, immagine del piatto.
Utile per stampa / spesa offline.

## Inserimento manuale ricette

Form per creare una ricetta manualmente (titolo, categoria, tempo, kcal, descrizione) con selezione ingredienti inline (nome, quantità, unità, gruppo macro). La ricetta salvata appare nell'elenco insieme a quelle importate automaticamente via recipe-scrapers, senza distinzione di origine.

## Integrazione dati mensa pubblica

Importare i menu settimanali da mense con dati pubblici e suggerire il pranzo in automatico basandosi su ciò che è disponibile quel giorno, evitando duplicati con la cena.

Riferimento mensa Tenaris (Pellegrini): `https://tenaris.pellegrinicloud.it/menu/1782805956/0/1605`

## Rimozione home-ai: integrazione diretta Groq

Eliminare la dipendenza dal proxy `home-ai` (endpoint `HOME_AI_URL`). Portare la chiamata AI direttamente in larder usando l'SDK Groq (`groq` Python package). La chiave API va in `.env` come `GROQ_API_KEY`. Questo semplifica il deploy e rimuove un punto di fallimento esterno.

## Prompt di allocazione personalizzabile

Permettere all'utente di modificare il prompt usato dall'AI per generare il piano pasti settimanale: es. regole dietetiche specifiche, preferenze stagionali, vincoli di budget, obiettivi macro. Il prompt personalizzato sovrascrive quello di default e viene salvato nel profilo utente.

## Dashboard utente e autenticazione

Meccanismo di login (JWT o sessioni) + dashboard personale con statistiche:
es. pasti pianificati, macros settimanali, ricette più usate.
Prerequisito per rendere l'app multi-utente e vendibile come SaaS.
