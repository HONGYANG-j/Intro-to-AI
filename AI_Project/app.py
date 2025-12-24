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
for k in ["cust_df", "loc_df", "order", "verified"]:
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
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(a))

def generate_qr(text):
    buf = io.BytesIO()
    qrcode.make(text).save(buf)
    buf.seek(0)
    return buf

def decode_qr(upload):
    try:
        pil_img = Image.open(upload).convert("L")
        img = np.array(pil_img)

        # Upscale + threshold (critical for Streamlit QR decoding)
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        _, img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)

        detector = cv2.QRCodeDetector()
        val, _, _ = detector.detectAndDecode(img)

        return val.strip() if val else None
    except Exception:
        return None

# =====================================================
# SIDEBAR UPLOADS
# =====================================================
with st.sidebar:
    st.header("📂 Upload CSV Files")

    cust = st.file_uploader("Customer.csv", type="csv")
    if cust:
        st.session_state.cust_df = normalize_cols(pd.read_csv(cust))
        st.success("Customer loaded")

    loc = st.file_uploader("Postcode + Location.csv", type="csv")
    if loc:
        st.session_state.loc_df = normalize_cols(pd.read_csv(loc))
        st.success("Postcode & Location loaded")

# =====================================================
# VALIDATION
# =====================================================
if (
    st.session_state.cust_df is None or
    st.session_state.loc_df is None
):
    st.warning("📌 Upload ALL required CSV files to continue")
    st.stop()

cust_df = st.session_state.cust_df
loc_df = st.session_state.loc_df

# =====================================================
# COLUMN SAFETY CHECKS
# =====================================================
required_customer = {"order id", "customer name", "postal code", "state"}
if not required_customer.issubset(cust_df.columns):
    st.error("Customer.csv must contain: order id, customer name, postal code, state")
    st.stop()

required_loc = {"postcode", "city_name", "latitude", "longitude"}
if not required_loc.issubset(loc_df.columns):
    st.error("Location CSV must contain: postcode, city_name, latitude, longitude")
    st.stop()

# =====================================================
# TABS
# =====================================================
tab1, tab2 = st.tabs(["🛒 Buy & Track", "🚚 Tracking Progress"])

# =====================================================
# TAB 1 – BUY & TRACK
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

    upload = st.file_uploader(
        "Upload QR",
        type=["png", "jpg"],
        key="qr_upload"
    )

    if upload:
        decoded = decode_qr(upload)

        if decoded is None:
            st.error("❌ Unable to read QR code. Please upload a clear QR image.")
        else:
            row = cust_df[cust_df["order id"].astype(str) == decoded]

            if not row.empty:
                st.session_state.order = row.iloc[0]
                st.session_state.verified = True
                st.success("QR verified successfully ✅")

                st.info("""
                👉 **Next Step**
                1. Click on **🚚 Tracking Progress** tab  
                2. View your real-time delivery status  

                If tracking does not appear, please contact support.
                """)

            else:
                st.error("""
                ❌ Order not found

                Please return to **Buy & Track** and place a new order.
                """)

# =====================================================
# TAB 2 – TRACKING
# =====================================================
with tab2:
    st.header("Delivery Tracking")

    if not st.session_state.verified:
        st.info("Upload & verify QR first.")
        st.stop()

    order = st.session_state.order
    postcode = str(order["postal code"])

    loc_row = loc_df[loc_df["postcode"].astype(str) == postcode]
    if loc_row.empty:
        st.error(f"Latitude/Longitude not found for postcode: {postcode}")
        st.stop()

    area = loc_row.iloc[0]["city_name"]
    home_lat = loc_row.iloc[0]["latitude"]
    home_lon = loc_row.iloc[0]["longitude"]

    port = (3.9767, 103.4242)   # Port Kuantan
    hub = (3.8168, 103.3317)    # Hub

    eta = (
        haversine(*port, *hub) / 70 +
        haversine(*hub, home_lat, home_lon) / 40
    )

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
    """)
