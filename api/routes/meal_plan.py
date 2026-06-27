from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from api.database import get_connection

router = APIRouter(prefix="/meal-plan", tags=["meal-plan"])


class MealPlanEntry(BaseModel):
    id: int
    date: str
    meal_type: str
    recipe_id: Optional[int] = None
    recipe_name: Optional[str] = None
    note: Optional[str] = None


class MealPlanCreate(BaseModel):
    date: str
    meal_type: str = "cena"
    recipe_id: Optional[int] = None
    note: Optional[str] = None


@router.get("/{date}", response_model=List[MealPlanEntry])
def get_meal_plan(date: str):
    conn = get_connection()
    rows = conn.execute(
        """SELECT mp.id, mp.date, mp.meal_type, mp.note, mp.recipe_id, r.name as recipe_name
           FROM meal_plan mp
           LEFT JOIN recipes r ON r.id = mp.recipe_id
           WHERE mp.date = ?
           ORDER BY mp.meal_type""",
        (date,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.post("/", response_model=MealPlanEntry, status_code=201)
def add_meal_plan(entry: MealPlanCreate):
    conn = get_connection()
    if entry.recipe_id:
        row = conn.execute("SELECT id FROM recipes WHERE id=?", (entry.recipe_id,)).fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Recipe not found")
    cursor = conn.execute(
        "INSERT INTO meal_plan (date, meal_type, recipe_id, note) VALUES (?,?,?,?)",
        (entry.date, entry.meal_type, entry.recipe_id, entry.note),
    )
    new_id = cursor.lastrowid
    conn.commit()
    row = conn.execute(
        """SELECT mp.id, mp.date, mp.meal_type, mp.note, mp.recipe_id, r.name as recipe_name
           FROM meal_plan mp LEFT JOIN recipes r ON r.id = mp.recipe_id
           WHERE mp.id=?""",
        (new_id,),
    ).fetchone()
    conn.close()
    return dict(row)


@router.delete("/{entry_id}", status_code=204)
def delete_meal_plan(entry_id: int):
    conn = get_connection()
    row = conn.execute("SELECT id FROM meal_plan WHERE id=?", (entry_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Entry not found")
    conn.execute("DELETE FROM meal_plan WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()
