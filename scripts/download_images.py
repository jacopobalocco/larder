#!/usr/bin/env python3
"""Scarica localmente le immagini di tutte le ricette e aggiorna image_id nel DB."""

import sqlite3
import urllib.request
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "recipes.db"
IMAGES_DIR = Path(__file__).parent.parent / "data" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/",
}


def ext_from_url(url: str) -> str:
    path = url.split("?")[0].lower()
    for e in (".webp", ".png", ".gif"):
        if path.endswith(e):
            return e
    return ".jpg"


def download(recipe_id: int, url: str) -> str | None:
    ext = ext_from_url(url)
    dest = IMAGES_DIR / f"{recipe_id}{ext}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        dest.write_bytes(data)
        return f"/images/{recipe_id}{ext}"
    except Exception as e:
        print(f"  ✗ {e}")
        return None


def main():
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT id, name, image_id FROM recipes ORDER BY id").fetchall()
    updated = 0
    for rid, name, img in rows:
        # Skip se già locale
        if img and img.startswith("/images/"):
            print(f"  ↩ ID {rid} già locale: {img}")
            continue
        if not img or not img.startswith("http"):
            print(f"  ⚠ ID {rid} ({name}): nessun URL immagine — skip")
            continue
        print(f"→ ID {rid} ({name})")
        local = download(rid, img)
        if local:
            conn.execute("UPDATE recipes SET image_id = ? WHERE id = ?", (local, rid))
            conn.commit()
            print(f"  ✓ {local}")
            updated += 1
        else:
            print(f"  ✗ fallito")

    conn.close()
    print(f"\n✅ {updated}/{len(rows)} immagini scaricate in {IMAGES_DIR}")


if __name__ == "__main__":
    main()
