# make_labels.py
#!/usr/bin/env python3
"""
Generate 1.5 in × 1 in Code-128 product labels
----------------------------------------------

* Reads inventory.csv  (barcode,name,variant,category,stock,…)
* Renders each barcode to PNG
* Lays them out on:
    • Letter sheet 5 × 10  (default)           OR
    • Roll-label page 1.5" × 1"

Requires: python-barcode[ pillow ], reportlab
"""

import os, math
from pathlib import Path

import pandas as pd
from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

################################################################################
# CONFIG – change here only
################################################################################
CSV_PATH     = Path("inventory.csv")
OUT_DIR      = Path("out")
PNG_DIR      = OUT_DIR / "png"

LABEL_W      = 1.5 * inch          # 1.5 inches
LABEL_H      = 1.0 * inch          # 1.0 inch

SHEET_MODE   = True                # True → Avery-style sheet, False → roll

# --- Sheet layout (Letter) ----------------------------------------------------
PAGE_SIZE    = letter              # 8.5 × 11 in
COLS         = 5
ROWS         = 10
MARGIN_L     = 0.25 * inch         # left/right margin
MARGIN_T     = 0.50 * inch         # top margin
GAP_X        = 0.125 * inch        # space between columns
GAP_Y        = 0.05  * inch        # space between rows (adjust to fit)

# --- Barcode inside the label -------------------------------------------------
CODE_W       = 1.3 * inch          # barcode graphic width
CODE_H       = 0.45 * inch
TEXT_OFFSET  = 0.08 * inch         # space between barcode & human text
FONT_SIZE    = 5.5
################################################################################


def render_pngs(df: pd.DataFrame):
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    df.columns = df.columns.str.strip()
    if "barcode" in df.columns:
        df["barcode"] = df["barcode"].astype(str)
    for code in df["barcode"]:
        out = PNG_DIR / f"{code}.png"
        if not out.exists():
            Code128(code, writer=ImageWriter()).save(out.with_suffix(""))


def make_sheet(df: pd.DataFrame):
    c = canvas.Canvas(str(OUT_DIR / "labels_sheet.pdf"), pagesize=PAGE_SIZE)
    page_w, page_h = PAGE_SIZE
    i = 0

    for _, row in df.iterrows():
        col = i % COLS
        row_idx = (i // COLS) % ROWS
        page_idx = i // (COLS * ROWS)

        # new page?
        if i and i % (COLS * ROWS) == 0:
            c.showPage()

        # top-left corner of current label
        x = MARGIN_L + col * (LABEL_W + GAP_X)
        y = page_h - MARGIN_T - LABEL_H - row_idx * (LABEL_H + GAP_Y)

        code = str(row["barcode"])
        img  = PNG_DIR / f"{code}.png"

        # draw barcode
        c.drawImage(str(img), x + (LABEL_W - CODE_W) / 2,
                    y + (LABEL_H - CODE_H - TEXT_OFFSET) / 2 + TEXT_OFFSET,
                    width=CODE_W, height=CODE_H)

        # draw human-readable line
        text = f"{row['name']} – {row['variant']}"
        c.setFont("Helvetica", FONT_SIZE)
        c.drawCentredString(x + LABEL_W / 2,
                            y + (LABEL_H - CODE_H) / 2 - TEXT_OFFSET,
                            text[:30])              # trim long names

        i += 1

    c.save()
    print(f"Saved → {OUT_DIR / 'labels_sheet.pdf'}")


def make_roll(df: pd.DataFrame):
    from reportlab.lib.pagesizes import landscape
    page_size = (LABEL_W, LABEL_H)
    c = canvas.Canvas(str(OUT_DIR / "labels_roll.pdf"), pagesize=page_size)

    for _, row in df.iterrows():
        code = str(row["barcode"])
        img  = PNG_DIR / f"{code}.png"

        # center graphic
        c.drawImage(str(img),
                    (LABEL_W - CODE_W) / 2,
                    (LABEL_H - CODE_H - TEXT_OFFSET) / 2 + TEXT_OFFSET,
                    width=CODE_W, height=CODE_H)

        c.setFont("Helvetica", FONT_SIZE)
        c.drawCentredString(LABEL_W / 2,
                            (LABEL_H - CODE_H) / 2 - TEXT_OFFSET,
                            f"{row['name']} – {row['variant']}"[:30])

        c.showPage()

    c.save()
    print(f"Saved → {OUT_DIR / 'labels_roll.pdf'}")


def generate_labels_pdf(
    csv_path: Path = CSV_PATH,
    out_dir: Path = OUT_DIR,
    sheet_mode: bool = SHEET_MODE,
) -> Path:
    """Generate labels PDF from ``csv_path``.

    Returns the path to the created PDF file.
    """
    out_dir.mkdir(exist_ok=True)
    df = pd.read_csv(csv_path, dtype=str)
    render_pngs(df)

    if sheet_mode:
        make_sheet(df)
        return out_dir / "labels_sheet.pdf"
    else:
        make_roll(df)
        return out_dir / "labels_roll.pdf"


def main():
    OUT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(CSV_PATH, dtype=str)
    render_pngs(df)

    if SHEET_MODE:
        make_sheet(df)
    else:
        make_roll(df)


if __name__ == "__main__":
    main()

