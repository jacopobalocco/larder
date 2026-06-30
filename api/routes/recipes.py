import json
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from api.database import get_connection
from api.models import Recipe, RecipeCreate


class RecipePatch(BaseModel):
    image_id: Optional[str] = None
    category: Optional[str] = None

router = APIRouter(prefix="/recipes", tags=["recipes"])


def _load_recipe(conn, row) -> dict:
    r = dict(row)
    r["tags"] = json.loads(r["tags"] or "[]")
    r["has_meat"] = bool(r["has_meat"])
    ing_rows = conn.execute(
        "SELECT name, quantity, unit, macro_group FROM recipe_ingredients WHERE recipe_id=? ORDER BY id",
        (r["id"],),
    ).fetchall()
    r["ingredients"] = [dict(i) for i in ing_rows]
    step_rows = conn.execute(
        "SELECT text FROM recipe_steps WHERE recipe_id=? ORDER BY step_number",
        (r["id"],),
    ).fetchall()
    r["steps"] = [s["text"] for s in step_rows]
    return r


@router.get("/", response_model=List[Recipe])
def list_recipes():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM recipes ORDER BY created_at DESC").fetchall()
    result = [_load_recipe(conn, row) for row in rows]
    conn.close()
    return result


@router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found")
    result = _load_recipe(conn, row)
    conn.close()
    return result


@router.post("/", response_model=Recipe, status_code=201)
def create_recipe(recipe: RecipeCreate):
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO recipes
               (name, description, category, time_min, servings,
                kcal, protein_g, carbs_g, fat_g, fiber_g,
                has_meat, image_id, tags)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            recipe.name, recipe.description, recipe.category, recipe.time_min,
            recipe.servings, recipe.kcal, recipe.protein_g, recipe.carbs_g,
            recipe.fat_g, recipe.fiber_g, int(recipe.has_meat),
            recipe.image_id, json.dumps(recipe.tags),
        ),
    )
    recipe_id = cursor.lastrowid
    for ing in recipe.ingredients:
        conn.execute(
            "INSERT INTO recipe_ingredients (recipe_id, name, quantity, unit, macro_group) VALUES (?,?,?,?,?)",
            (recipe_id, ing.name, ing.quantity, ing.unit, ing.macro_group),
        )
    for i, step in enumerate(recipe.steps, 1):
        conn.execute(
            "INSERT INTO recipe_steps (recipe_id, step_number, text) VALUES (?,?,?)",
            (recipe_id, i, step),
        )
    conn.commit()
    row = conn.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,)).fetchone()
    result = _load_recipe(conn, row)
    conn.close()
    return result


@router.patch("/{recipe_id}", response_model=Recipe)
def patch_recipe(recipe_id: int, patch: RecipePatch):
    conn = get_connection()
    row = conn.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found")
    fields = {k: v for k, v in {"image_id": patch.image_id, "category": patch.category}.items() if v is not None}
    if fields:
        sets = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE recipes SET {sets} WHERE id=?", (*fields.values(), recipe_id))
        conn.commit()
    result = _load_recipe(conn, conn.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,)).fetchone())
    conn.close()
    return result


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
    conn.commit()
    conn.close()
