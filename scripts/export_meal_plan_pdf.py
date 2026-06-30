#!/usr/bin/env python3
"""
Generate 3 PDF variants of the weekly meal plan.
Usage: uv run python scripts/export_meal_plan_pdf.py
Outputs: data/piano_pasti_A.pdf, _B.pdf, _C.pdf
"""
import io
import sqlite3
import tempfile
from collections import defaultdict
from datetime import date as Date
from pathlib import Path

from fpdf import FPDF as _FPDF
from PIL import Image


class FPDF(_FPDF):
    """FPDF with automatic Latin-1 sanitisation on all text output."""
    def cell(self, w=0, h=None, text="", **kwargs):
        return super().cell(w, h, safe(str(text)), **kwargs)
    def multi_cell(self, w, h=None, text="", **kwargs):
        return super().multi_cell(w, h, safe(str(text)), **kwargs)


class PianoFPDF(FPDF):
    """FPDF subclass with page footer for piano pasti PDF."""
    def footer(self):
        self.set_y(-13)
        self.set_draw_color(*MID_GRAY)
        self.set_line_width(0.2)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(1)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*GRAY)
        self.cell(90, 5, "Larder — piano generato automaticamente", align="L")
        self.cell(0, 5, f"pagina {self.page_no()}", align="R")

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "recipes.db"
OUT = ROOT / "data"

GIORNI = {0: "Lunedì", 1: "Martedì", 2: "Mercoledì", 3: "Giovedì",
          4: "Venerdì", 5: "Sabato", 6: "Domenica"}
MESI = {1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile", 5: "maggio",
        6: "giugno", 7: "luglio", 8: "agosto", 9: "settembre", 10: "ottobre",
        11: "novembre", 12: "dicembre"}

ORANGE = (194, 116, 90)
LIGHT_ORANGE = (252, 243, 239)
DARK = (35, 35, 35)
GRAY = (110, 110, 110)
LIGHT_GRAY = (247, 247, 247)
MID_GRAY = (210, 210, 210)
WHITE = (255, 255, 255)
GREEN = (80, 140, 100)
LIGHT_GREEN = (240, 249, 243)
BLUE = (70, 110, 160)
LIGHT_BLUE = (238, 244, 252)


def fmt_short(ds):
    d = Date.fromisoformat(ds)
    return f"{GIORNI[d.weekday()]} {d.day}"

def fmt_long(ds):
    d = Date.fromisoformat(ds)
    return f"{GIORNI[d.weekday()]} {d.day} {MESI[d.month]} {d.year}"

def safe(s: str) -> str:
    """Replace non-Latin-1 chars so fpdf built-in fonts don't choke."""
    return (s.replace("—", "-").replace("–", "-")
             .replace("…", "...").replace("•", "-")
             .replace("☐", "[ ]").replace("☑", "[x]")
             .replace("☀", ">>").replace("\U0001f319", ">>")
             .encode("latin-1", errors="replace").decode("latin-1"))

def trunc(s, n=55):
    return safe(s if len(s) <= n else s[:n - 1] + "...")


_img_cache: dict[str, str] = {}  # image_id -> resolved local path

def get_image_path(image_id: str | None) -> str | None:
    """Resolve /images/<id>.ext → local file path, converting webp if needed."""
    if not image_id:
        return None
    if image_id in _img_cache:
        return _img_cache[image_id]
    local = ROOT / "data" / image_id.lstrip("/")
    if not local.exists():
        return None
    if local.suffix.lower() == ".webp":
        # Convert webp → JPEG in a temp file
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        Image.open(local).convert("RGB").save(tmp.name, "JPEG")
        _img_cache[image_id] = tmp.name
        return tmp.name
    _img_cache[image_id] = str(local)
    return str(local)


def load_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT mp.date, mp.meal_type, r.id, r.name, r.category, r.time_min, r.kcal,
               r.protein_g, r.carbs_g, r.fat_g, r.image_id
        FROM meal_plan mp JOIN recipes r ON mp.recipe_id = r.id
        ORDER BY mp.date,
                 CASE mp.meal_type WHEN 'pranzo' THEN 0 ELSE 1 END,
                 r.category
    """).fetchall()
    ing_rows = conn.execute("""
        SELECT DISTINCT r.name AS recipe_name,
               ri.name AS ing, ri.quantity, ri.unit, ri.macro_group
        FROM meal_plan mp
        JOIN recipes r ON mp.recipe_id = r.id
        JOIN recipe_ingredients ri ON ri.recipe_id = r.id
        ORDER BY r.name, ri.macro_group, ri.name
    """).fetchall()
    conn.close()

    plan = defaultdict(lambda: defaultdict(list))
    for r in rows:
        plan[r["date"]][r["meal_type"]].append(dict(r))

    ings = defaultdict(list)
    seen = set()
    for r in ing_rows:
        key = (r["recipe_name"], r["ing"])
        if key not in seen:
            seen.add(key)
            ings[r["recipe_name"]].append(dict(r))

    return dict(sorted(plan.items())), dict(ings)


# ─── PDF A: Tabella settimanale ───────────────────────────────────────────────

def make_pdf_a(plan: dict) -> str:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── header ──────────────────────────────────────────────────────────────
    pdf.set_fill_color(*ORANGE)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Piano Pasti Settimanale", new_x="LMARGIN", new_y="NEXT",
             align="C", fill=True)

    dates = sorted(plan.keys())
    if dates:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*WHITE)
        pdf.set_fill_color(*ORANGE)
        week_label = safe(f"{fmt_long(dates[0])}  -  {fmt_long(dates[-1])}")
        pdf.cell(0, 6, week_label, new_x="LMARGIN", new_y="NEXT", align="C", fill=True)

    pdf.ln(5)

    # ── column headers ───────────────────────────────────────────────────────
    CW = [42, 85, 53]   # Giorno | Pranzo | Cena
    pdf.set_fill_color(*DARK)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 10)
    labels = ["GIORNO", "PRANZO", "CENA"]
    for lbl, w in zip(labels, CW):
        pdf.cell(w, 8, lbl, border=0, align="C", fill=True)
    pdf.ln()

    # ── rows ─────────────────────────────────────────────────────────────────
    row_h = 7
    for i, (dt, meals) in enumerate(sorted(plan.items())):
        fill = i % 2 == 0
        bg = LIGHT_GRAY if fill else WHITE

        pranzo_items = meals.get("pranzo", [])
        cena_items = meals.get("cena", [])

        def fmt_recipes(items):
            parts = []
            for r in items:
                mins = f" ({r['time_min']} min)" if r.get("time_min") else ""
                parts.append(trunc(r["name"], 48) + mins)
            return "\n".join(parts) if parts else "—"

        pranzo_txt = fmt_recipes(pranzo_items)
        cena_txt = fmt_recipes(cena_items)
        day_txt = fmt_short(dt)

        # measure max lines
        lines = max(pranzo_txt.count("\n") + 1, cena_txt.count("\n") + 1, 1)
        h = row_h * lines + 3

        y0 = pdf.get_y()
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*DARK)

        # Giorno
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_xy(15, y0)
        pdf.multi_cell(CW[0], h, day_txt, border=0, align="L", fill=True,
                       new_x="RIGHT", new_y="TOP")

        # Pranzo
        pdf.set_font("Helvetica", "", 8)
        pdf.set_xy(15 + CW[0], y0)
        pdf.multi_cell(CW[1], h, pranzo_txt, border=0, align="L", fill=True,
                       new_x="RIGHT", new_y="TOP")

        # Cena
        pdf.set_xy(15 + CW[0] + CW[1], y0)
        pdf.multi_cell(CW[2], h, cena_txt, border=0, align="L", fill=True,
                       new_x="LMARGIN", new_y="TOP")

        # separator line
        pdf.set_y(y0 + h)
        pdf.set_draw_color(*MID_GRAY)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())

    # ── footer ───────────────────────────────────────────────────────────────
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 5, "Larder — piano generato automaticamente", align="C")

    path = str(OUT / "piano_pasti_A_tabella.pdf")
    pdf.output(path)
    return path


# ─── PDF B: Griglia settimanale con foto (1 pagina) ───────────────────────────

_M          = 8       # page margin mm
_PW         = 210 - 2 * _M     # 194mm usable width
_GIORNO_W   = 22      # width of day-name column
_MEAL_TYPES = ["colazione", "pranzo", "cena"]
_MEAL_W     = (_PW - _GIORNO_W) / 3    # ~57.3mm per meal column
_IMG_PAD    = 3       # left/right padding inside each cell
_IMG_W      = _MEAL_W - 2 * _IMG_PAD   # ~51.3mm
_IMG_H      = 19      # fixed image height mm (same for every image)
_LABEL_H    = 2.5     # recipe name label height under image
_UNIT_H     = _IMG_H + _LABEL_H        # 21.5mm per image+label unit
_INTRA_GAP  = 1       # vertical gap between two stacked images
_ROW_PAD    = 2.5     # total row vertical padding (split ~1.25 top + 1.25 bottom)
_TITLE_H    = 10      # title block height
_COL_HDR_H  = 7       # column header row height


def _b_row_height(meals: dict) -> float:
    """Return height of a day row based on max dishes in any meal slot."""
    n = max((len(meals.get(mt, [])) for mt in _MEAL_TYPES), default=0)
    n = max(n, 1)
    return n * _UNIT_H + (n - 1) * _INTRA_GAP + _ROW_PAD


def make_pdf_b(plan: dict) -> str:
    pdf = PianoFPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(_M, _M, _M)
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    days = sorted(plan.items())

    # ── Title block ──────────────────────────────────────────────────────────
    y = _M
    pdf.set_fill_color(*ORANGE)
    pdf.rect(_M, y, 2, _TITLE_H - 1, style="F")            # orange left stripe

    pdf.set_xy(_M + 5, y + 1)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 5, "Piano Pasti Settimanale", new_x="LMARGIN", new_y="NEXT")

    if days:
        dates = [d for d, _ in days]
        pdf.set_x(_M + 5)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*GRAY)
        pdf.cell(0, 4, safe(f"{fmt_long(dates[0])}  -  {fmt_long(dates[-1])}"))

    y += _TITLE_H

    # ── Column headers ───────────────────────────────────────────────────────
    pdf.set_fill_color(*DARK)
    pdf.rect(_M, y, _PW, _COL_HDR_H, style="F")
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(*WHITE)
    # Giorno
    pdf.set_xy(_M, y)
    pdf.cell(_GIORNO_W, _COL_HDR_H, "GIORNO", align="C")
    # Meal columns
    for i, lbl in enumerate(["COLAZIONE", "PRANZO", "CENA"]):
        pdf.set_xy(_M + _GIORNO_W + i * _MEAL_W, y)
        pdf.cell(_MEAL_W, _COL_HDR_H, lbl, align="C")
    y += _COL_HDR_H

    # ── Day rows ─────────────────────────────────────────────────────────────
    for day_idx, (dt, meals) in enumerate(days):
        rh = _b_row_height(meals)
        d = Date.fromisoformat(dt)

        # row background (alternating)
        pdf.set_fill_color(*(LIGHT_ORANGE if day_idx % 2 == 0 else WHITE))
        pdf.rect(_M, y, _PW, rh, style="F")

        # day name (vertically centred)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(*DARK)
        pdf.set_xy(_M, y + rh / 2 - 5)
        pdf.cell(_GIORNO_W, 5, GIORNI[d.weekday()], align="C",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(_M)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(*GRAY)
        pdf.cell(_GIORNO_W, 4, f"{d.day} {MESI[d.month][:3]}", align="C")

        # meal cells
        for col_i, mt in enumerate(_MEAL_TYPES):
            x0 = _M + _GIORNO_W + col_i * _MEAL_W
            items = meals.get(mt, [])

            for img_i, recipe in enumerate(items):
                img_y = y + _ROW_PAD / 2 + img_i * (_UNIT_H + _INTRA_GAP)
                img_path = get_image_path(recipe.get("image_id"))

                if img_path:
                    try:
                        pdf.image(img_path, x=x0 + _IMG_PAD, y=img_y,
                                  w=_IMG_W, h=_IMG_H)
                    except Exception:
                        img_path = None
                if not img_path:
                    pdf.set_fill_color(*LIGHT_GRAY)
                    pdf.set_draw_color(*MID_GRAY)
                    pdf.rect(x0 + _IMG_PAD, img_y, _IMG_W, _IMG_H, style="FD")

                # recipe name label below image
                pdf.set_xy(x0 + _IMG_PAD, img_y + _IMG_H)
                pdf.set_font("Helvetica", "", 5)
                pdf.set_text_color(*GRAY)
                pdf.cell(_IMG_W, _LABEL_H, trunc(recipe["name"], 32), align="C")

        # grid lines for this row
        pdf.set_draw_color(*MID_GRAY)
        pdf.set_line_width(0.15)
        for col_i in range(1, 4):
            lx = _M + _GIORNO_W + (col_i - 1) * _MEAL_W
            pdf.line(lx, y, lx, y + rh)
        # bottom separator
        pdf.set_line_width(0.3 if day_idx < len(days) - 1 else 0.1)
        pdf.line(_M, y + rh, _M + _PW, y + rh)

        y += rh

    # outer border
    pdf.set_draw_color(*DARK)
    pdf.set_line_width(0.4)
    pdf.rect(_M, _M + _TITLE_H, _PW, _COL_HDR_H + sum(_b_row_height(m) for _, m in days),
             style="D")

    path = str(OUT / "piano_pasti_B_agenda.pdf")
    pdf.output(path)
    return path


# ─── PDF C: Meal prep kit con lista spesa ─────────────────────────────────────

def make_pdf_c(plan: dict, ings: dict) -> str:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=18)

    # ── cover page ───────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_fill_color(*GREEN)
    pdf.rect(0, 0, 210, 297, style="F")

    pdf.set_y(80)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 36)
    pdf.cell(0, 14, "Meal Prep", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, "Guida settimanale", new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.ln(8)
    dates = sorted(plan.keys())
    if dates:
        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(220, 240, 228)
        label = f"{fmt_long(dates[0])} – {fmt_long(dates[-1])}"
        pdf.cell(0, 8, label, new_x="LMARGIN", new_y="NEXT", align="C")

    # ── recipe pages ─────────────────────────────────────────────────────────
    for dt, meals in sorted(plan.items()):
        pdf.add_page()
        pdf.set_fill_color(*GREEN)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, f"  {fmt_long(dt).upper()}", new_x="LMARGIN", new_y="NEXT",
                 fill=True)
        pdf.ln(3)

        for meal_type in ["pranzo", "cena"]:
            items = meals.get(meal_type, [])
            if not items:
                continue

            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*GREEN)
            pdf.cell(0, 7, meal_type.upper(), new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(*GREEN)
            pdf.set_line_width(0.3)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(2)

            for recipe in items:
                name = recipe["name"]
                mins = recipe.get("time_min")
                kcal = recipe.get("kcal")

                # Recipe header
                pdf.set_fill_color(*LIGHT_GREEN)
                pdf.set_text_color(*DARK)
                pdf.set_font("Helvetica", "B", 9)
                meta_parts = []
                if mins:
                    meta_parts.append(f"{mins} min")
                if kcal:
                    meta_parts.append(f"{kcal} kcal")
                meta = "  |  ".join(meta_parts)
                pdf.cell(130, 6, trunc(name, 70), new_x="RIGHT", new_y="TOP",
                         fill=True)
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(*GRAY)
                pdf.cell(0, 6, meta, new_x="LMARGIN", new_y="NEXT",
                         fill=True, align="R")

                # Ingredients
                recipe_ings = ings.get(name, [])
                if recipe_ings:
                    pdf.set_font("Helvetica", "", 8)
                    pdf.set_text_color(*DARK)
                    col_w = 87
                    left_col = []
                    right_col = []
                    for j, ing in enumerate(recipe_ings):
                        qty = ing.get("quantity")
                        unit = ing.get("unit") or ""
                        qty_str = f"{int(qty) if qty and qty == int(qty) else qty} {unit}".strip() if qty else ""
                        bullet = f"- {ing['ing']}"
                        if qty_str:
                            bullet += f" — {qty_str}"
                        if j % 2 == 0:
                            left_col.append(bullet)
                        else:
                            right_col.append(bullet)

                    rows = max(len(left_col), len(right_col))
                    for k in range(rows):
                        y0 = pdf.get_y()
                        left_txt = left_col[k] if k < len(left_col) else ""
                        right_txt = right_col[k] if k < len(right_col) else ""
                        pdf.set_xy(18, y0)
                        pdf.cell(col_w, 4.5, trunc(left_txt, 46), new_x="RIGHT", new_y="TOP")
                        pdf.set_x(18 + col_w)
                        pdf.cell(col_w, 4.5, trunc(right_txt, 46), new_x="LMARGIN", new_y="NEXT")

                pdf.ln(3)

    # ── shopping list ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_fill_color(*DARK)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "  Lista della Spesa", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(4)

    # aggregate by macro_group
    shopping: dict[str, list[str]] = defaultdict(list)
    seen_ings: set[str] = set()
    for dt, meals in sorted(plan.items()):
        for meal_type in ["pranzo", "cena"]:
            for recipe in meals.get(meal_type, []):
                for ing in ings.get(recipe["name"], []):
                    key = ing["ing"].strip().lower()
                    if key not in seen_ings:
                        seen_ings.add(key)
                        qty = ing.get("quantity")
                        unit = ing.get("unit") or ""
                        qty_str = (f"{int(qty) if qty == int(qty) else qty} {unit}".strip()
                                   if qty else "")
                        label = ing["ing"]
                        if qty_str:
                            label += f" — {qty_str}"
                        shopping[ing.get("macro_group", "Altro")].append(label)

    GROUP_ORDER = ["Pasta/Riso", "Proteine", "Verdure", "Latticini",
                   "Condimenti", "Spezie", "Altro"]
    for group in GROUP_ORDER:
        items_list = shopping.get(group, [])
        if not items_list:
            continue
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*GREEN)
        pdf.cell(0, 7, group.upper(), new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(*GREEN)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*DARK)
        col_w = 87
        left = items_list[0::2]
        right = items_list[1::2]
        rows = max(len(left), len(right))
        for k in range(rows):
            y0 = pdf.get_y()
            l = f"[ ] {left[k]}" if k < len(left) else ""
            r = f"[ ] {right[k]}" if k < len(right) else ""
            pdf.set_xy(15, y0)
            pdf.cell(col_w, 5.5, trunc(l, 46), new_x="RIGHT", new_y="TOP")
            pdf.set_x(15 + col_w)
            pdf.cell(col_w, 5.5, trunc(r, 46), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # footer
    pdf.set_y(-18)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 5, "Larder — piano generato automaticamente", align="C")

    path = str(OUT / "piano_pasti_C_mealprep.pdf")
    pdf.output(path)
    return path


if __name__ == "__main__":
    plan, ings = load_data()
    print("Generating PDF A (tabella)...")
    print(" →", make_pdf_a(plan))
    print("Generating PDF B (agenda)...")
    print(" →", make_pdf_b(plan))
    print("Generating PDF C (meal prep kit)...")
    print(" →", make_pdf_c(plan, ings))
    print("Done.")
