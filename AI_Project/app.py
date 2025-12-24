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
# 0. PAGE CONFIGURATION & SESSION SETUP
# ==========================================
st.set_page_config(
    page_title="SmartTrack Logistics",
    layout="wide",
    page_icon="📦"
)

if "df_cust" not in st.session_state:
    st.session_state.df_cust = None
if "df_post" not in st.session_state:
    st.session_state.df_post = None
if "tracked_order" not in st.session_state:
    st.session_state.tracked_order = None

# ==========================================
# 1. STYLES
# ==========================================
st.markdown("""
<style>
.header-style {font-size:24px; font-weight:bold; color:#2E86C1;}
.info-box {padding:10px; background-color:#D6EAF8; border-radius:5px;}
.step {font-size:18px; margin-bottom:8px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. QR CODE FUNCTIONS
# ==========================================
def generate_qr_code(text):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
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
# 3. DISTANCE FUNCTION (FOR ETA)
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

# ==========================================
# 4. SIDEBAR – DATA UPLOAD
# ==========================================
with st.sidebar:
    st.header("⚙️ System Setup")

    cust_file = st.file_uploader("Upload Customer.csv", type="csv")
    if cust_file:
        st.session_state.df_cust = pd.read_csv(cust_file)
        st.success("Customer database loaded")

    post_file = st.file_uploader("Upload Malaysia_Postcode.csv", type="csv")
    if post_file:
        st.session_state.df_post = pd.read_csv(post_file)
        st.success("Postcode database loaded")

    st.caption("Group Project BSD3513")

if st.session_state.df_cust is None:
    st.warning("Please upload Customer.csv to continue.")
    st.stop()

df = st.session_state.df_cust

# ==========================================
# 5. MAIN TABS
# ==========================================
tab1, tab2 = st.tabs(["🛒 Page 1: Buy & Track", "🚚 Page 2: Delivery Progress"])

# ==========================================
# TAB 1 – BUY & TRACK
# ==========================================
with tab1:
    st.markdown('<p class="header-style">Customer Portal</p>', unsafe_allow_html=True)

    col_buy, col_track = st.columns(2)

    with col_buy:
        st.markdown('<div class="info-box"><b>Step A: Buy Item</b></div>', unsafe_allow_html=True)
        options = df["Order ID"].astype(str) + " | " + df["Customer Name"].astype(str)
        selected = st.selectbox("Choose an Order", options)

        if st.button("Confirm Purchase"):
            order_id = selected.split(" | ")[0]
            qr_img = generate_qr_code(order_id)
            st.image(qr_img, caption=f"Tracking ID: {order_id}")
            st.download_button("📥 Download QR Code", qr_img, f"{order_id}.png")

    with col_track:
        st.markdown('<div class="info-box"><b>Step B: Track Order</b></div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload QR Code Image", type=["png", "jpg", "jpeg"])

        if uploaded:
            scanned = decode_qr_code(uploaded)
            if scanned:
                record = df[df["Order ID"].astype(str) == scanned]
                if not record.empty:
