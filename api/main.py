from fastapi import FastAPI
from api.database import init_db
from api.routes.recipes import router as recipes_router

app = FastAPI(title="jb_wiki Recipes API", version="0.1.0")

app.include_router(recipes_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
