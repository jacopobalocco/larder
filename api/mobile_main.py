from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.database import init_db
from api.routes.meal_plan import router as meal_plan_router
from api.routes.meal_plan_ai import router as meal_plan_ai_router
from api.routes.recipes import router as recipes_router

app = FastAPI(title="Larder Mobile", version="0.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(recipes_router)
app.include_router(meal_plan_router)
app.include_router(meal_plan_ai_router)

IMAGES_DIR = Path(__file__).parent.parent / "data" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

FRONTEND = Path(__file__).parent.parent / "frontend" / "mobile.html"


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND)
