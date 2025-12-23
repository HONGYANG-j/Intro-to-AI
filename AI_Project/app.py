import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from math import radians, sin, cos, asin, sqrt
import qrcode
import cv2
import numpy as np
from PIL import Image
import io

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="SmartTrack Logistics",
    page_icon="📦",
    layout="wide"
)

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
.header-style {font-size:26px; font-weight:bold; color:#2E86C1;}
.info-box {padding:12px; background-color:#D6EAF8; border-radius:6px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# QR CODE FUNCTIONS (SAFE)
# ==========================================
def generate_qr_code(text):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def decode_qr_code(uploaded):
    image = Image.open(uploaded).convert("RGB")
    img = np.array(image)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    return data if data else None

# ==========================================
# SIDEBAR – DATA
# ==========================================
with st.sidebar:
    st.header("⚙️ System Setup")

    cust_file = st.file_uploader("Upload Customer.csv", type="csv")
    if cust_file:
        st.session_state.df_cust = pd.read_csv(cust_file)
        st.success("Customer data loaded")

    st.caption("BSD3513 Group Project")

if st.session_state.df_cust is None:
    st.warning("Please upload Customer.csv")
    st.stop()

df = st.session_state.df_cust

# ==========================================
# TABS
# ==========================================
tab1, tab2 = st.tabs(["🛒 Buy & Track", "🚚 Logistics Route"])

# ==========================================
# TAB 1 – BUY & TRACK
# ==========================================
with tab1:
    st.markdown('<p class="header-style">Customer Portal</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="info-box"><b>Step A: Buy Item</b></div>', unsafe_allow_html=True)

        options = df["Order ID"].astype(str) + " | " + df["Customer Name"]
        selected = st.selectbox("Select Order", options)

        if st.button("Generate QR Code"):
            order_id = selected.split(" | ")[0]
            qr = generate_qr_code(order_id)
            st.image(qr, caption=f"Tracking ID: {order_id}")
            st.download_button(
                "Download QR Code",
                qr,
                file_name=f"{order_id}.png",
                mime="image/png"
            )

    with col2:
        st.markdown('<div class="info-box"><b>Step B: Track Order</b></div>', unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload QR Code", type=["png", "jpg"])
        if uploaded:
            scanned = decode_qr_code(uploaded)

            if scanned:
                st.success(f"Order ID: {scanned}")
                record = df[df["Order ID"].astype(str) == scanned]

                if not record.empty:
                    st.session_state.tracked_order = record.iloc[0]
                    st.write("Customer:", record.iloc[0]["Customer Name"])
                    st.write("City:", record.iloc[0]["City"])
                    st.write("State:", record.iloc[0]["State"])
                else:
                    st.error("Order not found")
            else:
                st.error("QR not detected")

# ==========================================
# TAB 2 – LOGISTICS ROUTE (PAHANG ONLY)
# ==========================================
with tab2:
    st.markdown('<p class="header-style">Logistics Route (Pahang)</p>', unsafe_allow_html=True)

    order = st.session_state.tracked_order
    if order is None:
        st.info("Scan a QR code first")
        st.stop()

    # ONLY PAHANG
    if order["State"].lower() != "pahang":
        st.error("This system only supports Pahang deliveries")
        st.stop()

    # Locations
    PORT = ("Port Kuantan", 3.9767, 103.4242)
    HUB = ("Kuantan Hub", 3.8168, 103.3317)

    home_lat = HUB[1] + 0.15
    home_lon = HUB[2] + 0.15

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        return 2 * R * asin(sqrt(a))

    d1 = haversine(PORT[1], PORT[2], HUB[1], HUB[2])
    d2 = haversine(HUB[1], HUB[2], home_lat, home_lon)

    time = d1 / 80 + d2 / 60

    m = folium.Map(location=[HUB[1], HUB[2]], zoom_start=8)

    folium.Marker([PORT[1], PORT[2]], popup=PORT[0], icon=folium.Icon(color="blue")).add_to(m)
    folium.Marker([HUB[1], HUB[2]], popup=HUB[0], icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([home_lat, home_lon], popup=order["City"], icon=folium.Icon(color="red")).add_to(m)

    folium.PolyLine([(PORT[1], PORT[2]), (HUB[1], HUB[2])]).add_to(m)
    folium.PolyLine([(HUB[1], HUB[2]), (home_lat, home_lon)]).add_to(m)

    st_folium(m, width=900, height=500)

    st.metric("Estimated Delivery Time", f"{time:.2f} hours")
