import streamlit as st
import pandas as pd
import cv2
import numpy as np
from PIL import Image
import qrcode
import io
from math import radians, sin, cos, sqrt, asin

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config("SmartTrack Logistics", "📦", layout="wide")

# =====================================================
# SESSION STATE
# =====================================================
for k in ["cust_df", "pc_df", "loc_df", "order", "verified"]:
    if k not in st.session_state:
        st.session_state[k] = None if k != "verified" else False

# =====================================================
# UTILS
# =====================================================
def normalize_cols(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

def generate_qr(text):
    buf = io.BytesIO()
    qrcode.make(text).save(buf)
    buf.seek(0)
    return buf

def decode_qr(upload):
    img = cv2.cvtColor(np.array(Image.open(upload)), cv2.COLOR_RGB2GRAY)
    val, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    return val.strip() if val else None

# =====================================================
# SIDEBAR UPLOADS
# =====================================================
with st.sidebar:
    st.header("📂 Upload CSV Files")

    cust = st.file_uploader("Customer.csv", type="csv")
    if cust:
        st.session_state.cust_df = normalize_cols(pd.read_csv(cust))
        st.success("Customer loaded")

    pc = st.file_uploader("Postcode.csv", type=["csv", "txt"])
    if pc:
        df = pd.read_csv(pc, header=None, sep=None, engine="python")
        df.columns = ["postcode", "area", "city", "state"]
        st.session_state.pc_df = normalize_cols(df)
        st.success("Postcode loaded")

    loc = st.file_uploader("Latitude_Longitude.csv", type="csv")
    if loc:
        st.session_state.loc_df = normalize_cols(pd.read_csv(loc))
        st.success("Location loaded")

# =====================================================
# VALIDATION
# =====================================================
if (
    st.session_state.cust_df is None or
    st.session_state.pc_df is None or
    st.session_state.loc_df is None
):
    st.warning("📌 Upload ALL 3 CSV files to continue")
    st.stop()

cust_df = st.session_state.cust_df
pc_df = st.session_state.pc_df
loc_df = st.session_state.loc_df

# =====================================================
# COLUMN CHECKS (MATCH REAL DATA)
# =====================================================
required_customer = {
    "order id", "customer name", "postal code", "quantity"
}
if not required_customer.issubset(cust_df.columns):
    st.error("Customer.csv missing required columns")
    st.stop()

required_loc = {"states","district","town", "latitude", "longitude"}
if not required_loc.issubset(loc_df.columns):
    st.error("Latitude_Longitude.csv missing required columns")
    st.stop()

# =====================================================
# TABS
# =====================================================
tab1, tab2 = st.tabs(["🛒 Buy & Track", "🚚 Tracking Progress"])

# =====================================================
# TAB 1 – QR
# =====================================================
with tab1:
    st.header("Customer Portal")

    choice = st.selectbox(
        "Select Order",
        cust_df["order id"].astype(str) + " | " + cust_df["customer name"]
    )

    if st.button("Generate QR"):
        oid = choice.split(" | ")[0]
        qr = generate_qr(oid)
        st.image(qr)
        st.download_button("Download QR", qr, f"{oid}.png")

    upload = st.file_uploader("Upload QR", type=["png", "jpg"])
    if upload:
        decoded = decode_qr(upload)
        if decoded:
            row = cust_df[cust_df["order id"].astype(str) == decoded]
            if not row.empty:
                st.session_state.order = row.iloc[0]
                st.session_state.verified = True
                st.success("QR verified ✅")
            else:
                st.error("Order not found")

# =====================================================
# TAB 2 – TRACKING
# =====================================================
with tab2:
    st.header("Delivery Tracking")

    if not st.session_state.verified:
        st.info("Upload & verify QR first.")
        st.stop()

    order = st.session_state.order

    # 🔧 FIXED: correct column name
    postcode = str(order["postal code"])

    pc_row = pc_df[pc_df["postcode"].astype(str) == postcode]
    if pc_row.empty:
        st.error("Postcode not found")
        st.stop()

    area = pc_row.iloc[0]["area"]

    loc_row = loc_df[loc_df["area"] == area]
    if loc_row.empty:
        st.error("Latitude/Longitude not found")
        st.stop()

    home_lat = loc_row.iloc[0]["latitude"]
    home_lon = loc_row.iloc[0]["longitude"]

    # Fixed locations
    port = (3.9767, 103.4242)  # Port Kuantan
    hub = (3.8168, 103.3317)   # Kuantan Hub
    home = (home_lat, home_lon)

    d1 = haversine(*port, *hub)
    d2 = haversine(*hub, *home)
    total_distance = d1 + d2

    eta = d1 / 70 + d2 / 40

    # 💰 DELIVERY COST
    distance_cost = total_distance * 0.50
    quantity_cost = order["quantity"] * 2.0
    total_cost = distance_cost + quantity_cost

    steps = [
        "📦 Order Confirmed",
        "🚚 Picked Up from Port",
        "🏭 At Hub",
        "🛵 Out for Delivery",
        "✅ Delivered"
    ]

    current = 2
    for i, s in enumerate(steps):
        st.markdown(
            f"🔵 **{s}** _(Current)_" if i == current else
            f"✅ **{s}**" if i < current else
            f"⚪ {s}"
        )

    st.markdown("---")
    st.info(f"""
    **Order ID:** {order['order id']}  
    **Area:** {area}  
    **Home Location:** ({home_lat:.5f}, {home_lon:.5f})  
    **ETA:** ⏱ {eta:.2f} hours  
    **Estimated Cost:** 💰 RM {total_cost:.2f}
    """)
