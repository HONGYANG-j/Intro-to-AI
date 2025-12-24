import streamlit as st
import pandas as pd
import cv2
import numpy as np
from PIL import Image
import qrcode
import io
from math import radians, sin, cos, sqrt, asin

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="SmartTrack Logistics", layout="wide", page_icon="📦")

# ==========================================
# SESSION STATE
# ==========================================
for key in ["df", "order", "verified", "loc_df", "pc_df"]:
    if key not in st.session_state:
        st.session_state[key] = None

st.session_state.verified = st.session_state.verified or False

# ==========================================
# STYLES
# ==========================================
st.markdown("""
<style>
.header {font-size:26px; font-weight:bold; color:#1F618D;}
.box {padding:12px; background:#EBF5FB; border-radius:8px; margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# QR FUNCTIONS
# ==========================================
def generate_qr(text):
    qr = qrcode.make(text)
    buf = io.BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

def decode_qr(upload):
    img = Image.open(upload).convert("RGB")
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    data, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    return data.strip() if data else None

# ==========================================
# HAVERSINE DISTANCE
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

# ==========================================
# SIDEBAR UPLOADS
# ==========================================
with st.sidebar:
    st.header("⚙️ Data Setup")

    cust = st.file_uploader("Upload Customer.csv", type="csv")
    if cust:
        st.session_state.df = pd.read_csv(cust)
        st.success("Customer data loaded")

    loc = st.file_uploader("Upload Pahang Locations CSV", type="csv")
    if loc:
        st.session_state.loc_df = pd.read_csv(loc)
        st.success("Location data loaded")

    pc = st.file_uploader("Upload Pahang Postcode CSV", type="csv")
    if pc:
        st.session_state.pc_df = pd.read_csv(pc)
        st.success("Postcode data loaded")

if None in (st.session_state.df, st.session_state.loc_df, st.session_state.pc_df):
    st.warning("Please upload ALL required CSV files.")
    st.stop()

df = st.session_state.df

# ==========================================
# TABS
# ==========================================
tab1, tab2 = st.tabs(["🛒 Buy & Track", "🚚 Tracking Progress"])

# ==========================================
# TAB 1 – BUY & TRACK
# ==========================================
with tab1:
    st.markdown('<p class="header">Customer Portal</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        choice = st.selectbox(
            "Choose Order",
            df["Order ID"].astype(str) + " | " + df["Customer Name"]
        )

        if st.button("Generate QR"):
            oid = choice.split(" | ")[0]
            qr = generate_qr(oid)
            st.image(qr)
            st.download_button("Download QR", qr, f"{oid}.png")

    with col2:
        upload = st.file_uploader("Upload QR Code", type=["png", "jpg"])

        if upload:
            result = decode_qr(upload)
            if result:
                rec = df[df["Order ID"].astype(str) == result]
                if not rec.empty:
                    st.session_state.order = rec.iloc[0]
                    st.session_state.verified = True
                    st.success("QR verified successfully ✅")
                else:
                    st.error("Order not found")
            else:
                st.error("Invalid QR")

# ==========================================
# TAB 2 – DELIVERY TRACKING
# ==========================================
with tab2:
    st.markdown('<p class="header">Current Delivery Status</p>', unsafe_allow_html=True)

    if not st.session_state.verified:
        st.info("Please verify QR code on Page 1.")
        st.stop()

    order = st.session_state.order

    # Port & Hub
    port = (3.9767, 103.4242)
    hub = (3.8168, 103.3317)

    # Receiver location lookup
    area = st.session_state.pc_df[
        st.session_state.pc_df["postcode"] == order["Postcode"]
    ]["area"].values[0]

    loc = st.session_state.loc_df[
        st.session_state.loc_df["area"] == area
    ].iloc[0]

    home = (loc["latitude"], loc["longitude"])

    # Distance & ETA
    d1 = haversine(*port, *hub)
    d2 = haversine(*hub, *home)

    eta = d1 / 80 + d2 / 60  # hours

    # STATUS STEPS
    steps = [
        "📦 Order Confirmed",
        "🚚 Picked Up from Port",
        "🏭 At Hub (Kuantan)",
        "🛵 Out for Delivery",
        "✅ Delivered"
    ]

    current_step = 2

    st.markdown("### 📍 Tracking Progress")
    for i, step in enumerate(steps):
        if i < current_step:
            st.markdown(f"✅ **{step}**")
        elif i == current_step:
            st.markdown(f"🔵 **{step}** _(Current Status)_")
        else:
            st.markdown(f"⚪ {step}")

    st.markdown("---")
    st.info(f"""
📦 **Order ID:** {order['Order ID']}  
👤 **Customer:** {order['Customer Name']}  
📍 **Area:** {area}  
📌 **Latitude:** {home[0]:.5f}  
📌 **Longitude:** {home[1]:.5f}  

🚚 **Total Distance:** {(d1+d2):.2f} km  
⏱ **Estimated Delivery Time:** {eta:.2f} hours
""")
