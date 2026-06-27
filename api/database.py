import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "recipes.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS recipes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            description TEXT,
            category    TEXT    NOT NULL DEFAULT 'primi',
            time_min    INTEGER,
            servings    INTEGER NOT NULL DEFAULT 4,
            kcal        INTEGER,
            protein_g   INTEGER,
            carbs_g     INTEGER,
            fat_g       INTEGER,
            fiber_g     INTEGER,
            has_meat    INTEGER NOT NULL DEFAULT 0,
            image_id    TEXT,
            tags        TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id   INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
            name        TEXT    NOT NULL,
            quantity    REAL,
            unit        TEXT,
            macro_group TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recipe_steps (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id   INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
            step_number INTEGER NOT NULL,
            text        TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS meal_plan (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            meal_type   TEXT    NOT NULL DEFAULT 'cena',
            recipe_id   INTEGER REFERENCES recipes(id) ON DELETE SET NULL,
            note        TEXT
        );
    """)
    conn.commit()
    conn.close()
