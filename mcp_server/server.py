import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from api.database import get_connection, init_db

mcp = FastMCP("jb_wiki_recipes")


@mcp.tool()
def get_dinner_recipes() -> str:
    """Restituisce tutte le ricette disponibili per la cena nel database del database."""
    init_db()
    conn = get_connection()
    rows = conn.execute(
        "SELECT name, description, ingredients, prep_time_min, cook_time_min FROM recipes WHERE meal_type = 'dinner'"
    ).fetchall()
    conn.close()

    if not rows:
        return "Non ci sono ricette per la cena nel database."

    result = f"Ho trovato {len(rows)} ricetta/e per la cena:\n\n"
    for i, r in enumerate(rows, 1):
        result += f"**{i}. {r['name']}**\n"
        if r["description"]:
            result += f"   {r['description']}\n"
        result += f"   Ingredienti: {r['ingredients']}\n"
        if r["prep_time_min"] or r["cook_time_min"]:
            result += f"   Tempo: {r['prep_time_min'] or 0} min prep + {r['cook_time_min'] or 0} min cottura\n"
        result += "\n"
    return result


@mcp.tool()
def list_all_recipes() -> str:
    """Elenca tutte le ricette nel database colazione, pranzo, cena)."""
    init_db()
    conn = get_connection()
    rows = conn.execute("SELECT id, name, meal_type, prep_time_min, cook_time_min FROM recipes").fetchall()
    conn.close()

    if not rows:
        return "Il database delle ricette è vuoto."

    result = f"Ricette totali: {len(rows)}\n\n"
    for r in rows:
        total = (r["prep_time_min"] or 0) + (r["cook_time_min"] or 0)
        result += f"- [{r['id']}] {r['name']} ({r['meal_type']}) — {total} min totali\n"
    return result


@mcp.tool()
def search_recipes(query: str) -> str:
    """Cerca ricette nel database per nome o ingrediente.

    Args:
        query: termine di ricerca (nome del piatto o ingrediente)
    """
    init_db()
    conn = get_connection()
    rows = conn.execute(
        "SELECT name, description, ingredients, meal_type FROM recipes WHERE name LIKE ? OR ingredients LIKE ?",
        (f"%{query}%", f"%{query}%"),
    ).fetchall()
    conn.close()

    if not rows:
        return f"Nessuna ricetta trovata per '{query}'."

    result = f"Ricette trovate per '{query}':\n\n"
    for r in rows:
        result += f"**{r['name']}** ({r['meal_type']})\n"
        if r["description"]:
            result += f"   {r['description']}\n"
        result += f"   Ingredienti: {r['ingredients']}\n\n"
    return result


if __name__ == "__main__":
    mcp.run()
