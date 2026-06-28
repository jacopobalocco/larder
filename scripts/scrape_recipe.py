#!/usr/bin/env python3
"""Scrapa una ricetta da URL e stampa i dati in JSON su stdout."""

import json
import sys
import urllib.request

from recipe_scrapers import scrape_html


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "usage: scrape_recipe.py <url>"}))
        sys.exit(1)

    url = sys.argv[1]
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )

    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
    except Exception as e:
        print(json.dumps({"error": f"fetch failed: {e}"}))
        sys.exit(1)

    try:
        s = scrape_html(html, org_url=url)
    except Exception as e:
        print(json.dumps({"error": f"scrape failed: {e}"}))
        sys.exit(1)

    data = {
        "name": s.title(),
        "time_min": s.total_time() or None,
        "servings_raw": s.yields(),
        "image": s.image(),
        "ingredients": s.ingredients(),
        "steps": s.instructions_list(),
        "nutrients": {},
    }
    try:
        data["nutrients"] = s.nutrients()
    except Exception:
        pass

    print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
