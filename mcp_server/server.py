import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from api.database import get_connection, init_db

mcp = FastMCP("larder_recipes")


def _fmt_recipe(r, ingredients, steps) -> str:
    lines = [f"**{r['name']}** (ID {r['id']})"]
    lines.append(f"  Categoria: {r['category']} | Tempo: {r['time_min'] or '?'} min | Porzioni: {r['servings']}")
    if r["description"]:
        lines.append(f"  {r['description']}")
    if r["kcal"]:
        lines.append(f"  Kcal: {r['kcal']} | Proteine: {r['protein_g']}g | Carbs: {r['carbs_g']}g | Grassi: {r['fat_g']}g")
    tags = json.loads(r["tags"] or "[]")
    if tags:
        lines.append(f"  Tag: {', '.join(tags)}")
    if ingredients:
        ing_str = ", ".join(
            f"{i['quantity'] or 'q.b.'} {i['unit'] or ''} {i['name']}".strip()
            for i in ingredients
        )
        lines.append(f"  Ingredienti: {ing_str}")
    if steps:
        lines.append("  Procedimento:")
        for n, s in enumerate(steps, 1):
            lines.append(f"    {n}. {s['text']}")
    return "\n".join(lines)


@mcp.tool()
def list_all_recipes() -> str:
    """Elenca tutte le ricette salvate nel database (con categoria e tempo)."""
    init_db()
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, category, time_min, servings, has_meat FROM recipes ORDER BY category, name"
    ).fetchall()
    conn.close()

    if not rows:
        return "Il database delle ricette è vuoto."

    by_cat: dict[str, list] = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)

    lines = [f"Ricette totali: {len(rows)}\n"]
    for cat, recipes in sorted(by_cat.items()):
        lines.append(f"### {cat.capitalize()}")
        for r in recipes:
            meat = " 🥩" if r["has_meat"] else ""
            lines.append(f"  [{r['id']}] {r['name']}{meat} — {r['time_min'] or '?'} min")
    return "\n".join(lines)


@mcp.tool()
def get_recipe(recipe_id: int) -> str:
    """Restituisce i dettagli completi di una ricetta (ingredienti e passi).

    Args:
        recipe_id: ID numerico della ricetta
    """
    init_db()
    conn = get_connection()
    r = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if not r:
        conn.close()
        return f"Nessuna ricetta trovata con ID {recipe_id}."
    ingredients = conn.execute(
        "SELECT * FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,)
    ).fetchall()
    steps = conn.execute(
        "SELECT * FROM recipe_steps WHERE recipe_id = ? ORDER BY step_number", (recipe_id,)
    ).fetchall()
    conn.close()
    return _fmt_recipe(r, ingredients, steps)


@mcp.tool()
def get_meal_plan(date: str) -> str:
    """Restituisce il programma pasti per una data specifica (formato YYYY-MM-DD).

    Args:
        date: data nel formato YYYY-MM-DD (es. "2026-06-28")
    """
    init_db()
    conn = get_connection()
    rows = conn.execute(
        """SELECT mp.meal_type, mp.note, r.id, r.name, r.category, r.time_min, r.servings,
                  r.kcal, r.protein_g, r.carbs_g, r.fat_g, r.tags, r.description
           FROM meal_plan mp
           LEFT JOIN recipes r ON r.id = mp.recipe_id
           WHERE mp.date = ?
           ORDER BY mp.meal_type""",
        (date,),
    ).fetchall()
    conn.close()

    if not rows:
        return f"Nessun pasto programmato per il {date}."

    lines = [f"Programma del {date}:\n"]
    for row in rows:
        meal = row["meal_type"].capitalize()
        if row["id"]:
            lines.append(f"**{meal}**: {row['name']} (ID {row['id']}) — {row['category']}, {row['time_min'] or '?'} min")
        else:
            lines.append(f"**{meal}**: {row['note'] or '(nessuna ricetta associata)'}")
    return "\n".join(lines)


@mcp.tool()
def suggest_dinner() -> str:
    """Suggerisce cosa cucinare a cena: elenca tutte le ricette con dettagli completi."""
    init_db()
    conn = get_connection()
    rows = conn.execute("SELECT * FROM recipes ORDER BY RANDOM()").fetchall()
    if not rows:
        conn.close()
        return "Il database delle ricette è vuoto."

    lines = [f"Hai {len(rows)} ricette disponibili. Ecco qualche idea per stasera:\n"]
    for r in rows[:5]:
        ingredients = conn.execute(
            "SELECT * FROM recipe_ingredients WHERE recipe_id = ?", (r["id"],)
        ).fetchall()
        lines.append(_fmt_recipe(r, ingredients, []))
        lines.append("")
    conn.close()
    return "\n".join(lines)


@mcp.tool()
def search_recipes(query: str) -> str:
    """Cerca ricette per nome, ingrediente o tag.

    Args:
        query: termine di ricerca (es. "pasta", "pomodoro", "vegano")
    """
    init_db()
    conn = get_connection()
    rows = conn.execute(
        """SELECT DISTINCT r.* FROM recipes r
           LEFT JOIN recipe_ingredients i ON i.recipe_id = r.id
           WHERE r.name LIKE ? OR r.description LIKE ? OR r.tags LIKE ? OR i.name LIKE ?
           ORDER BY r.name""",
        tuple(f"%{query}%" for _ in range(4)),
    ).fetchall()
    conn.close()

    if not rows:
        return f"Nessuna ricetta trovata per '{query}'."

    lines = [f"Trovate {len(rows)} ricette per '{query}':\n"]
    for r in rows:
        meat = " 🥩" if r["has_meat"] else ""
        lines.append(f"  [{r['id']}] {r['name']}{meat} ({r['category']}) — {r['time_min'] or '?'} min")
    return "\n".join(lines)


@mcp.tool()
def create_recipe(
    name: str,
    category: str,
    steps: list[str],
    description: str = "",
    time_min: int = 0,
    servings: int = 4,
    kcal: int = 0,
    protein_g: int = 0,
    carbs_g: int = 0,
    fat_g: int = 0,
    fiber_g: int = 0,
    has_meat: bool = False,
    tags: list[str] = [],
    ingredients: list[dict] = [],
) -> str:
    """Crea una nuova ricetta nel database.

    Args:
        name: nome della ricetta
        category: categoria (primi, secondi, contorni, zuppe, dolci, colazione)
        steps: lista di passi del procedimento
        description: descrizione opzionale
        time_min: tempo di preparazione in minuti
        servings: numero di porzioni
        kcal: calorie per porzione
        protein_g: proteine in grammi
        carbs_g: carboidrati in grammi
        fat_g: grassi in grammi
        fiber_g: fibre in grammi
        has_meat: contiene carne
        tags: lista di tag (es. ["vegano", "veloce"])
        ingredients: lista di dict con chiavi: name, quantity (float|null), unit (str|null), macro_group
    """
    init_db()
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO recipes
               (name, description, category, time_min, servings,
                kcal, protein_g, carbs_g, fat_g, fiber_g,
                has_meat, tags)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (name, description or None, category, time_min or None, servings,
         kcal or None, protein_g or None, carbs_g or None, fat_g or None, fiber_g or None,
         int(has_meat), json.dumps(tags)),
    )
    recipe_id = cursor.lastrowid
    for ing in ingredients:
        conn.execute(
            "INSERT INTO recipe_ingredients (recipe_id, name, quantity, unit, macro_group) VALUES (?,?,?,?,?)",
            (recipe_id, ing["name"], ing.get("quantity"), ing.get("unit"), ing.get("macro_group", "Altro")),
        )
    for i, step in enumerate(steps, 1):
        conn.execute(
            "INSERT INTO recipe_steps (recipe_id, step_number, text) VALUES (?,?,?)",
            (recipe_id, i, step),
        )
    conn.commit()
    conn.close()
    return f"Ricetta '{name}' creata con ID {recipe_id}."


@mcp.tool()
def update_recipe_image(recipe_id: int, image_id: str) -> str:
    """Aggiorna l'immagine di una ricetta.

    Args:
        recipe_id: ID della ricetta
        image_id: URL o ID immagine (Unsplash photo ID o path /images/...)
    """
    init_db()
    conn = get_connection()
    row = conn.execute("SELECT id, name FROM recipes WHERE id=?", (recipe_id,)).fetchone()
    if not row:
        conn.close()
        return f"Ricetta con ID {recipe_id} non trovata."
    conn.execute("UPDATE recipes SET image_id=? WHERE id=?", (image_id, recipe_id))
    conn.commit()
    conn.close()
    return f"Immagine della ricetta '{row['name']}' (ID {recipe_id}) aggiornata."


@mcp.tool()
def delete_recipe(recipe_id: int) -> str:
    """Elimina una ricetta dal database (ingredienti e passi inclusi).

    Args:
        recipe_id: ID della ricetta da eliminare
    """
    init_db()
    conn = get_connection()
    row = conn.execute("SELECT id, name FROM recipes WHERE id=?", (recipe_id,)).fetchone()
    if not row:
        conn.close()
        return f"Ricetta con ID {recipe_id} non trovata."
    name = row["name"]
    conn.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
    conn.commit()
    conn.close()
    return f"Ricetta '{name}' (ID {recipe_id}) eliminata."


@mcp.tool()
def add_meal_plan(date: str, meal_type: str, recipe_id: int = 0, note: str = "") -> str:
    """Aggiunge un pasto al piano settimanale.

    Args:
        date: data in formato YYYY-MM-DD (es. "2026-06-28")
        meal_type: tipo di pasto ("pranzo" o "cena")
        recipe_id: ID della ricetta (0 = nessuna ricetta, solo nota)
        note: nota opzionale
    """
    init_db()
    conn = get_connection()
    rid = recipe_id if recipe_id > 0 else None
    if rid:
        row = conn.execute("SELECT name FROM recipes WHERE id=?", (rid,)).fetchone()
        if not row:
            conn.close()
            return f"Ricetta con ID {recipe_id} non trovata."
        recipe_name = row["name"]
    else:
        recipe_name = note or "(nessuna ricetta)"
    cursor = conn.execute(
        "INSERT INTO meal_plan (date, meal_type, recipe_id, note) VALUES (?,?,?,?)",
        (date, meal_type, rid, note or None),
    )
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return f"Aggiunto {meal_type} del {date}: {recipe_name} (entry ID {entry_id})."


@mcp.tool()
def delete_meal_plan_entry(entry_id: int) -> str:
    """Elimina un'entry dal piano pasti tramite il suo ID.

    Args:
        entry_id: ID dell'entry del piano pasti (ottenibile con get_meal_plan)
    """
    init_db()
    conn = get_connection()
    row = conn.execute(
        """SELECT mp.id, mp.date, mp.meal_type, r.name as recipe_name
           FROM meal_plan mp LEFT JOIN recipes r ON r.id = mp.recipe_id
           WHERE mp.id=?""",
        (entry_id,),
    ).fetchone()
    if not row:
        conn.close()
        return f"Entry con ID {entry_id} non trovata."
    conn.execute("DELETE FROM meal_plan WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()
    return f"Rimosso {row['meal_type']} del {row['date']} ({row['recipe_name'] or 'nota'}) — entry ID {entry_id}."


if __name__ == "__main__":
    mcp.run()
