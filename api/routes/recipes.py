from fastapi import APIRouter, HTTPException
from typing import List
from api.database import get_connection
from api.models import Recipe, RecipeCreate

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("/", response_model=List[Recipe])
def list_recipes():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM recipes ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/dinner", response_model=List[Recipe])
def get_dinner_recipes():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM recipes WHERE meal_type = 'dinner' ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return dict(row)


@router.post("/", response_model=Recipe, status_code=201)
def create_recipe(recipe: RecipeCreate):
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO recipes (name, description, ingredients, instructions, meal_type, prep_time_min, cook_time_min)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (recipe.name, recipe.description, recipe.ingredients, recipe.instructions,
         recipe.meal_type, recipe.prep_time_min, recipe.cook_time_min),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM recipes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    conn.commit()
    conn.close()
