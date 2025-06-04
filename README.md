
# Inventory Scanner (Streamlit)

A minimal Streamlit app that lets you subtract stock levels by scanning
barcodes with a _keyboard‑wedge_ (USB/Bluetooth HID) barcode scanner.

## Quick start

```bash
git clone <this‑repo>
cd inventory_scanner
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Place your **inventory.csv** in the same folder as `app.py`. Each row is:

| barcode | name | variant | category | stock |
|---------|------|---------|----------|-------|

When the scanner sends digits + **Enter**, the form auto‑submits and
decrements `stock` (never below 0).

## Columns explained

* **barcode** – numeric or alphanumeric string the scanner outputs.
* **name / variant / category** – shown for humans.
* **stock** – integer. The dashboard highlights rows with ≤ slider value.

## Customising

* **Add SKU lookup**: merge with a products table on `variant_id`.
* **Increase security**: run behind Nginx with basic‑auth or Streamlit‑auth‑component.
* **Deploy**: Dockerfile → Streamlit Community Cloud, Fly.io, or on‑prem.

--
