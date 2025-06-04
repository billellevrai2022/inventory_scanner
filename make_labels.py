# make_labels.py
import pandas as pd, os
from barcode import Code128
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import letter

df = pd.read_csv("inventory.csv")          # must include 'barcode','name','variant'

# 1. render each barcode to PNG ------------------------------------------------
os.makedirs("out/png", exist_ok=True)
for _, row in df.iterrows():
    code = str(row["barcode"])
    Code128(code, writer=ImageWriter()).save(f"out/png/{code}")

# 2. lay them onto Avery 5160 (30-up) sheet ------------------------------------
c = canvas.Canvas("out/labels.pdf", pagesize=letter)
x0, y0 = 5 * mm, 8 * mm              # top-left margin of first label
w, h   = 66 * mm, 24 * mm            # label size
cols, rows = 3, 10

i = 0
for _, row in df.iterrows():
    col = i % cols
    row_idx = i // cols
    if row_idx == rows:              # new page
        c.showPage(); row_idx = 0
    x = x0 + col * w
    y = letter[1] - y0 - (row_idx + 1) * h
    c.drawImage(f"out/png/{row['barcode']}.png", x + 2*mm, y + 6*mm, width=40*mm, height=12*mm)
    c.setFont("Helvetica", 6)
    c.drawString(x + 2*mm, y + 2*mm, f"{row['name']} – {row['variant']}")
    i += 1

c.save()
print("PDF ready: out/labels.pdf")
