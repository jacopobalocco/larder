import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.database import init_db, get_connection

RECIPES = [
    {
        "name": "Pasta al Pomodoro",
        "description": "Un classico intramontabile della cucina italiana",
        "ingredients": "320g spaghetti, 400g pomodori pelati, 2 spicchi d'aglio, basilico fresco, olio EVO, sale",
        "instructions": "1. Soffriggere l'aglio in olio. 2. Aggiungere i pomodori e cuocere 20 min. 3. Lessare la pasta, scolare e mantecare col sugo. 4. Servire con basilico fresco.",
        "meal_type": "dinner",
        "prep_time_min": 10,
        "cook_time_min": 25,
    },
    {
        "name": "Risotto ai Funghi Porcini",
        "description": "Cremoso risotto autunnale con porcini secchi e freschi",
        "ingredients": "320g riso Carnaroli, 50g porcini secchi, 200g porcini freschi, 1 cipolla, 1L brodo vegetale, parmigiano, burro, vino bianco",
        "instructions": "1. Ammollare i porcini secchi 30 min. 2. Rosolare cipolla e funghi. 3. Tostare il riso, sfumare col vino. 4. Aggiungere il brodo un mestolo alla volta. 5. Mantecare con burro e parmigiano.",
        "meal_type": "dinner",
        "prep_time_min": 35,
        "cook_time_min": 20,
    },
    {
        "name": "Pollo al Limone",
        "description": "Petto di pollo succulento in salsa al limone",
        "ingredients": "600g petti di pollo, 2 limoni, aglio, rosmarino, olio EVO, farina, brodo di pollo, sale e pepe",
        "instructions": "1. Infarinare il pollo. 2. Dorare in padella con olio e aglio. 3. Sfumare col succo di limone. 4. Aggiungere brodo e rosmarino. 5. Cuocere 15 min a fuoco medio.",
        "meal_type": "dinner",
        "prep_time_min": 10,
        "cook_time_min": 20,
    },
]


def seed():
    init_db()
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    if count > 0:
        print(f"DB already has {count} recipes, skipping seed.")
        conn.close()
        return
    for r in RECIPES:
        conn.execute(
            """INSERT INTO recipes (name, description, ingredients, instructions, meal_type, prep_time_min, cook_time_min)
               VALUES (:name, :description, :ingredients, :instructions, :meal_type, :prep_time_min, :cook_time_min)""",
            r,
        )
    conn.commit()
    conn.close()
    print(f"Seeded {len(RECIPES)} recipes.")


if __name__ == "__main__":
    seed()
