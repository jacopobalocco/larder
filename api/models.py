from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Ingredient(BaseModel):
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    macro_group: str


class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "primi"
    time_min: Optional[int] = None
    servings: int = 4
    kcal: Optional[int] = None
    protein_g: Optional[int] = None
    carbs_g: Optional[int] = None
    fat_g: Optional[int] = None
    fiber_g: Optional[int] = None
    has_meat: bool = False
    image_id: Optional[str] = None
    tags: List[str] = []


class RecipeCreate(RecipeBase):
    ingredients: List[Ingredient] = []
    steps: List[str] = []


class Recipe(RecipeBase):
    id: int
    created_at: Optional[datetime] = None
    ingredients: List[Ingredient] = []
    steps: List[str] = []

    model_config = {"from_attributes": True}
