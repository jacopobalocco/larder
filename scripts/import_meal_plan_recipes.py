#!/usr/bin/env python3
"""Import massivo ricette dal piano alimentare — scraping + POST al DB."""

import json
import re
import urllib.request
import urllib.error

from recipe_scrapers import scrape_html

API = "http://localhost:PORT"

RECIPES = [
    # Pranzi
    # ID 3 già importata — skip
    # {"url": "https://ricetta.it/insalata-di-quinoa-con-pollo-e-verdure",      "category": "secondi",  "has_meat": True},
    {"url": "https://ricette.giallozafferano.it/Salmone-agli-agrumi-con-riso-pilaf.html", "category": "secondi", "has_meat": True},
    {"url": "https://ricette.giallozafferano.it/Pappardelle-al-ragu-di-lenticchie-e-funghi.html", "category": "primi", "has_meat": False},
    {"url": "https://www.cucchiaio.it/ricetta/omelette-spinaci-e-funghi/",     "category": "secondi",  "has_meat": False},
    {"url": "https://www.misya.info/ricetta/riso-e-fagioli.htm",               "category": "primi",    "has_meat": False},
    {"url": "https://ricette.giallozafferano.it/Couscous-verdure-e-ceci-con-Bimby.html", "category": "primi", "has_meat": False},
    {"url": "https://www.misya.info/ricetta/tofu-strapazzato.htm",             "category": "secondi",  "has_meat": False},
    # Cene
    {"url": "https://ricette.giallozafferano.it/Branzino-agli-agrumi-con-patate-novelle-al-rosmarino-e-zucchine-prezzemolate.html", "category": "secondi", "has_meat": True},
    {"url": "https://ricette.giallozafferano.it/Pasta-e-fagioli-alla-napoletana.html", "category": "zuppe",  "has_meat": False},
    {"url": "https://ricette.giallozafferano.it/Frittata-di-zucchine-con-provola.html", "category": "secondi", "has_meat": False},
    {"url": "https://ricette.giallozafferano.it/Spaghetti-alle-noci.html",     "category": "primi",    "has_meat": False},
    {"url": "https://ricette.giallozafferano.it/Zuppa-di-farro-e-borlotti.html", "category": "zuppe",  "has_meat": False},
    {"url": "https://www.misya.info/ricetta/melanzane-ripiene.htm",            "category": "secondi",  "has_meat": False},
]

VERDURE = {"zucchin", "melanzane", "peperon", "carota", "carote", "cipolla", "cipoll",
           "pomodor", "spinaci", "broccol", "sedano", "funghi", "aglio", "porro",
           "zucca", "carciofi", "cavolfi", "lattuga", "insalata", "rucola"}
PROTEINE = {"pollo", "salmone", "branzino", "tonno", "uova", "uovo", "tofu", "lenticch",
            "fagioli", "ceci", "borlotti", "cannellini", "tempeh"}
PASTA_RISO = {"pasta", "riso", "farro", "orzo", "couscous", "quinoa", "pappardell",
              "spaghetti", "rigatoni", "penne", "fusilli", "gnocchi"}
LATTICINI = {"mozzarella", "parmigiano", "ricotta", "provola", "pecorino",
             "yogurt", "latte", "burro", "formaggio", "grana"}
SPEZIE = {"sale", "pepe", "curcuma", "paprika", "cannella", "origano", "basilico",
          "rosmarino", "timo", "prezzemolo", "menta", "curry", "noce moscat",
          "alloro", "zafferano", "coriandolo", "zenzero", "peperoncino"}
CONDIMENTI = {"olio", "aceto", "limone", "vino", "brodo", "acqua", "senape",
              "passata", "concentrato"}


def macro_group(name: str) -> str:
    n = name.lower()
    if any(k in n for k in PASTA_RISO): return "Pasta/Riso"
    if any(k in n for k in LATTICINI):  return "Latticini"
    if any(k in n for k in PROTEINE):   return "Proteine"
    if any(k in n for k in VERDURE):    return "Verdure"
    if any(k in n for k in SPEZIE):     return "Spezie"
    if any(k in n for k in CONDIMENTI): return "Condimenti"
    return "Altro"


def parse_ingredient(raw: str) -> dict:
    raw = raw.strip()
    # "Nome ingrediente 300 g" o "300 g Nome"
    m = re.search(r'(\d+(?:[,\.]\d+)?)\s*(g|ml|kg|cl|l|cucchiai|cucchiaino|cucchiaini|spicch\w*|fett\w*|foglie|rametti|mazzo|mazzi|pezzi|fila|filetti?|unità|tazze?|bicchieri?|pizzico)\b', raw, re.IGNORECASE)
    quantity = float(m.group(1).replace(",", ".")) if m else None
    unit = m.group(2).lower() if m else None
    # Rimuovi la parte numerica per ottenere il nome pulito
    name = re.sub(r'\d+(?:[,\.]\d+)?\s*(?:g|ml|kg|cl|l|cucchiai|cucchiaino|cucchiaini|spicch\w*|fett\w*|foglie|rametti|mazzo|mazzi|pezzi|fila|filetti?|unità|tazze?|bicchieri?|pizzico)\b', '', raw, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name).strip(' ,.-')
    if not name:
        name = raw
    return {"name": name, "quantity": quantity, "unit": unit, "macro_group": macro_group(name)}


def scrape(url: str) -> dict | None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
    except Exception as e:
        print(f"  ✗ fetch: {e}")
        return None
    try:
        s = scrape_html(html, org_url=url)
        data = {
            "name": s.title(),
            "time_min": s.total_time() or None,
            "servings_raw": s.yields() or "",
            "image": s.image(),
            "ingredients": s.ingredients(),
            "steps": s.instructions_list(),
        }
        try: data["nutrients"] = s.nutrients()
        except: data["nutrients"] = {}
        return data
    except Exception as e:
        print(f"  ✗ scrape: {e}")
        return None


def servings_int(raw: str) -> int:
    m = re.search(r'\d+', raw or "")
    return int(m.group()) if m else 4


def post_recipe(payload: dict) -> int | None:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{API}/recipes/",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())["id"]
    except urllib.error.HTTPError as e:
        print(f"  ✗ POST {e.code}: {e.read().decode()[:200]}")
        return None


def main():
    results = []
    for entry in RECIPES:
        url = entry["url"]
        print(f"\n→ {url}")
        data = scrape(url)
        if not data:
            results.append({"url": url, "status": "FAIL (scrape)"})
            continue

        nutrients = data.get("nutrients", {}) or {}
        payload = {
            "name": data["name"],
            "description": None,
            "category": entry["category"],
            "time_min": data["time_min"],
            "servings": servings_int(data["servings_raw"]),
            "kcal": round(float(re.search(r'[\d\.]+', nutrients["calories"]).group())) if nutrients.get("calories") else None,
            "protein_g": round(float(re.search(r'[\d\.]+', nutrients["proteinContent"]).group())) if nutrients.get("proteinContent") else None,
            "carbs_g": round(float(re.search(r'[\d\.]+', nutrients["carbohydrateContent"]).group())) if nutrients.get("carbohydrateContent") else None,
            "fat_g": round(float(re.search(r'[\d\.]+', nutrients["fatContent"]).group())) if nutrients.get("fatContent") else None,
            "fiber_g": round(float(re.search(r'[\d\.]+', nutrients["fiberContent"]).group())) if nutrients.get("fiberContent") else None,
            "has_meat": entry["has_meat"],
            "image_id": data["image"],
            "tags": [],
            "ingredients": [parse_ingredient(i) for i in data["ingredients"]],
            "steps": data["steps"],
        }

        recipe_id = post_recipe(payload)
        if recipe_id:
            print(f"  ✓ salvata — ID {recipe_id}: {data['name']}")
            results.append({"id": recipe_id, "name": data["name"], "url": url, "status": "OK"})
        else:
            results.append({"url": url, "name": data.get("name"), "status": "FAIL (POST)"})

    print("\n\n=== RIEPILOGO ===")
    ok = [r for r in results if r["status"] == "OK"]
    fail = [r for r in results if r["status"] != "OK"]
    print(f"Importate: {len(ok)}/13")
    if fail:
        print("\nFallite:")
        for r in fail:
            print(f"  ✗ {r.get('name', r['url'])} — {r['status']}")


if __name__ == "__main__":
    main()
