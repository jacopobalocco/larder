from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: str
    instructions: str
    meal_type: str = "dinner"
    prep_time_min: Optional[int] = None
    cook_time_min: Optional[int] = None


class RecipeCreate(RecipeBase):
    pass


class Recipe(RecipeBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
