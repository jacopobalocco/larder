import json
import os
from typing import List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.database import get_connection

router = APIRouter(prefix="/meal-plan", tags=["meal-plan-ai"])

HOME_AI_URL = os.getenv("HOME_AI_URL", "http://localhost:8766/complete")
FAMILY_PROFILE = os.getenv(
    "FAMILY_PROFILE",
    "Nessun profilo familiare configurato: nessun vincolo di età, allergia o obiettivo di salute noto.",
)


class RecipeInfo(BaseModel):
    id: int
    name: str
    category: str
    has_meat: bool = False
    tags: List[str] = []
    kcal: Optional[int] = None
    protein_g: Optional[int] = None
    carbs_g: Optional[int] = None
    fat_g: Optional[int] = None
    ingredients: List[str] = []


class AutoDistributeRequest(BaseModel):
    slots: List[str]
    recipes: List[RecipeInfo]


class AutoDistributeResponse(BaseModel):
    plan: dict


def _build_prompt(slots: List[str], recipes: List[RecipeInfo]) -> str:
    recipes_json = json.dumps(
        [
            {
                "id": r.id,
                "nome": r.name,
                "categoria": r.category,
                "ha_carne": r.has_meat,
                "tag": r.tags,
                "kcal": r.kcal,
                "proteine_g": r.protein_g,
                "carboidrati_g": r.carbs_g,
                "grassi_g": r.fat_g,
                "ingredienti": r.ingredients,
            }
            for r in recipes
        ],
        ensure_ascii=False,
        indent=2,
    )

    return f"""Sei un assistente per la pianificazione alimentare di una famiglia italiana.

FAMIGLIA:
{FAMILY_PROFILE}

VINCOLI SETTIMANALI (obbligatori, conteggiati su tutti gli slot insieme):
- Carne (rossa o bianca): max 1 ricetta in tutta la settimana
- Pesce: max 1 ricetta in tutta la settimana
- Formaggio come proteina principale: max 1 ricetta in tutta la settimana
- Uova come proteina principale: max 1 ricetta in tutta la settimana
- Tutti gli altri slot devono usare proteine vegetali (legumi, tofu, cereali, tempeh)

REGOLA COMPOSIZIONE SLOT:
- Se la ricetta ha categoria "piatto_unico" → va assegnata da sola allo slot (array con 1 solo id)
- Altrimenti ogni slot deve contenere: 1 primo (categoria "primi" o "zuppe") + 1 secondo (categoria "secondi") + opzionalmente 1 contorno (categoria "contorni") se il secondo non lo integra già

RICETTE DISPONIBILI:
{recipes_json}

SLOT DA RIEMPIRE:
{json.dumps(slots, ensure_ascii=False)}

OUTPUT: rispondi SOLO con JSON valido, nessun testo aggiuntivo, nessun markdown.
Formato: {{"slot": [id1, id2], ...}}
Esempio: {{"lun-pranzo": [5, 12], "lun-cena": [7], "mar-cena": [3, 8]}}
Regole:
- Ogni ricetta al massimo una volta
- Usa solo ID presenti nella lista ricette
- Includi solo gli slot che riesci a riempire correttamente con le ricette disponibili"""


@router.post("/auto-distribute", response_model=AutoDistributeResponse)
async def auto_distribute(req: AutoDistributeRequest):
    if not req.recipes or not req.slots:
        return AutoDistributeResponse(plan={})

    prompt = _build_prompt(req.slots, req.recipes)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(HOME_AI_URL, json={"prompt": prompt, "json_mode": True})
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"home-ai non raggiungibile: {e}")

    raw = resp.json().get("result", "")
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="home-ai ha restituito JSON non valido")

    valid_ids = {r.id for r in req.recipes}
    clean_plan = {}
    for slot, ids in plan.items():
        if slot in req.slots and isinstance(ids, list):
            valid = [i for i in ids if isinstance(i, int) and i in valid_ids]
            if valid:
                clean_plan[slot] = valid

    return AutoDistributeResponse(plan=clean_plan)


# ── AUTO-PLAN: seleziona e distribuisce dalla libreria completa ───────────────

class AutoPlanRequest(BaseModel):
    slots: List[str]
    excluded_ids: List[int] = []


class AutoPlanResponse(BaseModel):
    plan: dict


def _build_auto_plan_prompt(slots: List[str], recipes: List[RecipeInfo]) -> str:
    recipes_json = json.dumps(
        [
            {
                "id": r.id,
                "nome": r.name,
                "categoria": r.category,
                "ha_carne": r.has_meat,
                "tag": r.tags,
                "kcal": r.kcal,
                "proteine_g": r.protein_g,
                "carboidrati_g": r.carbs_g,
                "grassi_g": r.fat_g,
            }
            for r in recipes
        ],
        ensure_ascii=False,
        indent=2,
    )

    return f"""Sei un assistente per la pianificazione alimentare settimanale di una famiglia italiana.

FAMIGLIA:
{FAMILY_PROFILE}

VINCOLI SETTIMANALI (obbligatori, su tutti gli slot):
- Carne (rossa o bianca): max 1 ricetta in tutta la settimana
- Pesce: max 1 ricetta in tutta la settimana
- Formaggio come proteina principale: max 1 ricetta in tutta la settimana
- Uova come proteina principale: max 1 ricetta in tutta la settimana
- Restanti slot: proteine vegetali (legumi, tofu, cereali, tempeh)

REGOLA COMPOSIZIONE SLOT:
- Ricetta con categoria "piatto_unico" → va da sola (array con 1 id)
- Altrimenti: 1 primo (categoria "primi" o "zuppe") + 1 secondo (categoria "secondi") + opzionale 1 contorno

RICETTE DISPONIBILI (scegli solo da questa lista):
{recipes_json}

SLOT DA PIANIFICARE:
{json.dumps(slots, ensure_ascii=False)}

OBIETTIVO: scegli le ricette più adatte da questa lista e assegnale agli slot rispettando tutti i vincoli. Non è obbligatorio riempire ogni slot se le ricette non bastano. Privilegia varietà e bilanciamento nutrizionale. Per i pranzi preferisci ricette ad alto contenuto di carboidrati e proteine.

OUTPUT: SOLO JSON valido, nessun testo aggiuntivo, nessun markdown.
Formato: {{"slot": [id1, id2], ...}}
Esempio: {{"lun-pranzo": [5, 12], "lun-cena": [7], "mar-cena": [3, 8]}}
- Ogni ricetta al massimo una volta
- Usa solo ID dalla lista ricette"""


@router.post("/auto-plan", response_model=AutoPlanResponse)
async def auto_plan(req: AutoPlanRequest):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM recipes").fetchall()
    conn.close()

    excluded = set(req.excluded_ids)
    recipes = [
        RecipeInfo(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            has_meat=bool(row["has_meat"]),
            tags=json.loads(row["tags"] or "[]"),
            kcal=row["kcal"],
            protein_g=row["protein_g"],
            carbs_g=row["carbs_g"],
            fat_g=row["fat_g"],
        )
        for row in rows
        if row["id"] not in excluded
    ]

    if not recipes or not req.slots:
        return AutoPlanResponse(plan={})

    prompt = _build_auto_plan_prompt(req.slots, recipes)

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(HOME_AI_URL, json={"prompt": prompt, "json_mode": True})
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"home-ai non raggiungibile: {e}")

    raw = resp.json().get("result", "")
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="home-ai ha restituito JSON non valido")

    valid_ids = {r.id for r in recipes}
    clean_plan = {}
    for slot, ids in plan.items():
        if slot in req.slots and isinstance(ids, list):
            valid = [i for i in ids if isinstance(i, int) and i in valid_ids]
            if valid:
                clean_plan[slot] = valid

    return AutoPlanResponse(plan=clean_plan)
