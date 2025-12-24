import streamlit as st
import pandas as pd
import cv2
import numpy as np
from PIL import Image
import qrcode
import io
import time
from math import radians, sin, cos, sqrt, asin

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="SmartTrack Logistics", layout="wide", page_icon="📦")

# ==========================================
# SESSION STATE
# ==========================================
if "df_cust" not in st.session_state:
    st.session_state.df_cust = None
if "tracked_order" not in st.session_state:
    st.session_state.tracked_order = None

# ==========================================
# STYLES
# ==========================================
st.markdown("""
<style>
.header-style {font-size:24px; font-weight:bold; color:#2E86C1;}
.info-box {padding:10px; background-color:#D6EAF8; border-radius:5px;}
.step {font-size:18px; margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# QR CODE FUNCTIONS
# ==========================================
def generate_qr_code(text):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def decode_qr_code(uploaded_image):
    try:
        image = Image.open(uploaded_image).convert("RGB")
    except:
        return None

    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)

    return data.strip() if data else None

# ==========================================
# DISTANCE FUNCTION (ETA)
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ System Setup")
    cust_file = st.file_uploader("Upload Customer.csv", type="csv")
    if cust_file:
        st.session_state.df_cust = pd.read_csv(cust_file)
        st.success("Customer database loaded")
    st.caption("Group Project BSD3513")

if st.session_state.df_cust is None:
    st.warning("Please upload Customer.csv")
    st.stop()

df = st.session_state.df_cust

# ==========================================
# TABS
# ==========================================
tab1, tab2 = st.tabs(["🛒 Buy & Track", "🚚 Delivery Progress"])

# ==========================================
# TAB 1
# ==========================================
with tab1:
    st.markdown('<p class="header-style">Customer Portal</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="info-box"><b>Step A: Buy Item</b></div>', unsafe_allow_html=True)
        options = df["Order ID"].astype(str) + " | " + df["Customer Name"].astype(str)
        selected = st.selectbox("Select Order", options)

        if st.button("Confirm Purchase"):
            order_id = selected.split(" | ")[0]
            qr = generate_qr_code(order_id)
            st.image(qr, caption=f"Tracking ID: {order_id}")
            st.download_button("Download QR", qr, f"{order_id}.png")

    with col2:
        st.markdown('<div class="info-box"><b>Step B: Track Order</b></div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload QR Code", type=["png", "jpg", "jpeg"])

        if uploaded:
            scanned = decode_qr_code(uploaded)
            if scanned:
                record = df[df["Order ID"].astype(str) == scanned]

                if not record.empty:
                    st.session_state.tracked_order = record.iloc[0]
                    st.success(f"Order {scanned} found")
                else:
                    st.error("Order not found")
            else:
                st.error("QR code not readable")

# ==========================================
# TAB 2 – A → B → C PROGRESS
# ==========================================
with tab2:
    st.markdown('<p class="header-style">Delivery Progress</p>', unsafe_allow_html=True)

    order = st.session_state.tracked_order
    if order is None:
        st.info("Scan a QR code first")
        st.stop()

    # FIXED LOCATIONS
    port = ("Port Kuantan", 3.9767, 103.4242)
    hub = ("Parcel Hub Kuantan", 3.8168, 103.3317)
    home = (f"Customer Home ({order['City']})", hub[1] + 0.12, hub[2] + 0.12)

    d1 = haversine(port[1], port[2], hub[1], hub[2])
    d2 = haversine(hub[1], hub[2], home[1], home[2])

    t1 = d1 / 80
    t2 = d2 / 60
    total_time = t1 + t2

    st.markdown("### 📦 Route")
    st.markdown(f"""
    <div class="step">🚢 {port[0]}</div>
    <div class="step">⬇️</div>
    <div class="step">🏭 {hub[0]}</div>
    <div class="step">⬇️</div>
    <div class="step">🏠 {home[0]}</div>
    """, unsafe_allow_html=True)

    st.markdown("### ⏳ Delivery Progress")
    bar = st.progress(0)

    for i in range(101):
        time.sleep(0.02)
        bar.progress(i)

    st.success("✅ Parcel Delivered")
    st.metric("Estimated Delivery Time", f"{total_time:.2f} hours")
