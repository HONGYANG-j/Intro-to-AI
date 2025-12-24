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
if "df" not in st.session_state:
    st.session_state.df = None
if "order" not in st.session_state:
    st.session_state.order = None
if "verified" not in st.session_state:
    st.session_state.verified = False

# ==========================================
# STYLES
# ==========================================
st.markdown("""
<style>
.header {font-size:26px; font-weight:bold; color:#1F618D;}
.box {padding:12px; background:#EBF5FB; border-radius:8px; margin-bottom:10px;}
.status {font-size:18px; font-weight:bold;}
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
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    return data.strip() if data else None

# ==========================================
# DISTANCE (ETA)
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
    st.header("⚙️ Setup")
    file = st.file_uploader("Upload Customer.csv", type="csv")
    if file:
        st.session_state.df = pd.read_csv(file)
        st.success("Data loaded")

if st.session_state.df is None:
    st.warning("Upload Customer.csv to continue")
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
        st.markdown('<div class="box">Step 1: Select Order</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="box">Step 2: Upload QR to Track</div>', unsafe_allow_html=True)
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
    st.markdown('<p class="header">Live Delivery Tracking</p>', unsafe_allow_html=True)

    if not st.session_state.verified:
        st.info("""
        📌 **Instructions**
        1. Go to Page 1  
        2. Upload your QR code  
        3. Verify the order  
        4. Come back here to track delivery
        """)
        st.stop()

    order = st.session_state.order

    # LOCATIONS
    port = (3.9767, 103.4242)
    hub = (3.8168, 103.3317)
    home = (hub[0] + 0.12, hub[1] + 0.12)

    d1 = haversine(*port, *hub)
    d2 = haversine(*hub, *home)
    eta = d1/80 + d2/60

    # STATUS STEPS
    statuses = [
        "📦 Order Confirmed",
        "🚢 Picked up from Port Kuantan",
        "🏭 Arrived at Hub",
        "🛵 Out for Delivery",
        "✅ Delivered"
    ]

    st.markdown("### 📍 Current Delivery Status")

    status_box = st.empty()
    progress = st.progress(0)

    for i in range(100):
        time.sleep(0.03)
        progress.progress(i+1)

        if i < 20:
            status_box.markdown(f"<p class='status'>{statuses[0]}</p>", unsafe_allow_html=True)
        elif i < 45:
            status_box.markdown(f"<p class='status'>{statuses[1]}</p>", unsafe_allow_html=True)
        elif i < 65:
            status_box.markdown(f"<p class='status'>{statuses[2]}</p>", unsafe_allow_html=True)
        elif i < 85:
            status_box.markdown(f"<p class='status'>{statuses[3]}</p>", unsafe_allow_html=True)
        else:
            status_box.markdown(f"<p class='status'>{statuses[4]}</p>", unsafe_allow_html=True)

    st.success("🎉 Parcel successfully delivered")
    st.metric("Estimated Delivery Time", f"{eta:.2f} hours")
