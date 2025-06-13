
import streamlit as st
import pandas as pd
from pathlib import Path
import base64

import make_labels

st.set_page_config(page_title="Inventory Scanner", page_icon="📦", layout="wide")

DATA_PATH = Path(__file__).with_name("inventory.csv")

@st.cache_data(show_spinner=False)
def load_inventory(path):
    df = pd.read_csv(path, dtype=str)
    df.columns = df.columns.str.strip()
    if "stock" in df.columns:
        df["stock"] = df["stock"].astype(int)
    else:
        print("Warning: 'stock' column not found in the CSV.")
    return df


def save_inventory(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)

st.title("📦 Inventory Scanner Dashboard")

df = load_inventory(DATA_PATH)

# --- Scan form -----------------------------------------------------------
with st.form("scan_form", clear_on_submit=True):
    barcode = st.text_input("Scan barcode", key="barcode_input")
    submitted = st.form_submit_button("Submit")
    if submitted:
        code = barcode.strip()
        if code == "":
            st.warning("No barcode received.")
        elif code in df["barcode"].values:
            idx = df.index[df["barcode"] == code][0]
            df.at[idx, "stock"] = max(df.at[idx, "stock"] - 1, 0)
            product_name = df.at[idx, "name"]
            new_stock = df.at[idx, "stock"]
            st.success(f"✓ {product_name} → new stock: {new_stock}")
            save_inventory(df, DATA_PATH)
        else:
            st.error(f"Unknown barcode: {code}")

# --- Dashboard -----------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.header("Current Inventory")
    st.dataframe(df, use_container_width=True, hide_index=True)

with col2:
    st.header("Low / Out‑of‑stock items")
    low = st.slider("Threshold", 0, 20, 0)
    low_df = df[df["stock"] <= low]
    st.dataframe(low_df, use_container_width=True, hide_index=True)

# Pie chart of stock by category
by_cat = df.groupby("category")["stock"].sum()
st.subheader("Stock distribution by category")
st.bar_chart(by_cat)

# --- Label generator ----------------------------------------------------
st.header("Generate Labels")
if st.button("Create Labels PDF"):
    pdf_path = make_labels.generate_labels_pdf(DATA_PATH)
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    b64 = base64.b64encode(pdf_bytes).decode()
    pdf_embed = f"<iframe id='pdf_frame' src='data:application/pdf;base64,{b64}' width='700' height='500'></iframe>"
    print_button = """
        <button onclick="document.getElementById('pdf_frame').contentWindow.print();">
            Print labels
        </button>
    """
    st.markdown(pdf_embed + print_button, unsafe_allow_html=True)

