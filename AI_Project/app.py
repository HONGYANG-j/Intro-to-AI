import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import cv2
import numpy as np
from PIL import Image
import qrcode
import io

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
if "tracked_order" not in st.session_state:
    st.session_state.tracked_order = None

# ==========================================
# 1. STYLES
# ==========================================

st.markdown("""
<style>
.header-style {font-size:24px; font-weight:bold; color:#2E86C1;}
.info-box {padding:10px; background-color:#D6EAF8; border-radius:5px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. QR CODE FUNCTIONS
# ==========================================

def generate_qr_code(text):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=4
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def decode_qr_code(uploaded_image):
    image = Image.open(uploaded_image).convert("RGB")
    img = np.array(image)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    return data if data else None

# ==========================================
# 3. SIDEBAR – DATA UPLOAD
# ==========================================

with st.sidebar:
    st.header("⚙️ System Setup")

    cust_file = st.file_uploader("Upload Customer.csv", type="csv")
    if cust_file:
        st.session_state.df_cust = pd.read_csv(cust_file)
        st.success("Customer database loaded")

    st.caption("Group Project BSD3513")

if st.session_state.df_cust is None:
    st.warning("Please upload Customer dataset.")
    st.stop()

df = st.session_state.df_cust

# ==========================================
# 4. MAIN TABS
# ==========================================

tab1, tab2 = st.tabs(
    ["🛒 Page 1: Buy & Track", "🗺️ Page 2: Logistics Route"]
)

# ==========================================
# TAB 1 – BUY & TRACK
# ==========================================

with tab1:
    st.markdown('<p class="header-style">Customer Portal</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="info-box"><b>Step A: Buy Item</b></div>', unsafe_allow_html=True)

        options = df["Order ID"].astype(str) + " | " + df["Customer Name"]
        selected = st.selectbox("Choose an Order", options)

        if st.button("Confirm Purchase"):
            order_id = selected.split(" | ")[0]
            qr = generate_qr_code(order_id)
            st.image(qr, caption=f"Tracking ID: {order_id}")
            st.download_button(
                "📥 Download QR Code",
                qr,
                file_name=f"{order_id}_QR.png",
                mime="image/png"
            )

    with col2:
        st.markdown('<div class="info-box"><b>Step B: Track Order</b></div>', unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload QR Code", type=["png", "jpg", "jpeg"])
        if uploaded:
            scanned = decode_qr_code(uploaded)
            if scanned:
                st.success(f"Order ID: {scanned}")
                record = df[df["Order ID"].astype(str) == scanned]
                if not record.empty:
                    st.session_state.tracked_order = record.iloc[0]
                    st.info("Go to Page 2 to view delivery route")
            else:
                st.error("QR Code not detected")

# ==========================================
# TAB 2 – LOGISTICS ROUTE (PAHANG ONLY)
# ==========================================

PORT_KUANTAN = ("Port Kuantan", 3.9767, 103.4242)
KUANTAN_HUB = ("Kuantan Hub", 3.8168, 103.3317)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

with tab2:
    st.markdown('<p class="header-style">Logistics Route (Pahang Only)</p>', unsafe_allow_html=True)

    order = st.session_state.tracked_order
    if order is None:
        st.info("Please scan QR code first.")
        st.stop()

    # Fake customer coordinates near Kuantan
    home_lat = KUANTAN_HUB[1] + 0.12
    home_lon = KUANTAN_HUB[2] + 0.12

    d1 = haversine(PORT_KUANTAN[1], PORT_KUANTAN[2], KUANTAN_HUB[1], KUANTAN_HUB[2])
    d2 = haversine(KUANTAN_HUB[1], KUANTAN_HUB[2], home_lat, home_lon)

    total_time = (d1 / 80) + (d2 / 60)

    m = folium.Map(location=[KUANTAN_HUB[1], KUANTAN_HUB[2]], zoom_start=8)

    # Markers
    folium.Marker(
        [PORT_KUANTAN[1], PORT_KUANTAN[2]],
        popup="🚢 Port Kuantan",
        icon=folium.Icon(color="blue", icon="ship", prefix="fa")
    ).add_to(m)

    folium.Marker(
        [KUANTAN_HUB[1], KUANTAN_HUB[2]],
        popup="🏭 Kuantan Hub",
        icon=folium.Icon(color="green", icon="warehouse", prefix="fa")
    ).add_to(m)

    folium.Marker(
        [home_lat, home_lon],
        popup="🏠 Customer",
        icon=folium.Icon(color="red", icon="home", prefix="fa")
    ).add_to(m)

    # Routes
    folium.PolyLine(
        [(PORT_KUANTAN[1], PORT_KUANTAN[2]), (KUANTAN_HUB[1], KUANTAN_HUB[2])],
        color="blue",
        tooltip="Port → Hub"
    ).add_to(m)

    folium.PolyLine(
        [(KUANTAN_HUB[1], KUANTAN_HUB[2]), (home_lat, home_lon)],
        color="green",
        tooltip="Hub → Customer"
    ).add_to(m)

    # 🚚 Vehicle icon (static)
    folium.Marker(
        [KUANTAN_HUB[1], KUANTAN_HUB[2]],
        icon=folium.CustomIcon(
            "https://cdn-icons-png.flaticon.com/512/1995/1995470.png",
            icon_size=(40, 40)
        )
    ).add_to(m)

    st_folium(m, width=900, height=500)

    st.metric("⏱️ Estimated Delivery Time", f"{total_time:.2f} hours")
