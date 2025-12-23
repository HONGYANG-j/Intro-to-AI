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

# =====================================================
# 1. PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="SmartTrack Logistics – Pahang Hub",
    layout="wide",
    page_icon="📦"
)

# =====================================================
# 2. SESSION STATE
# =====================================================
if "df_cust" not in st.session_state:
    st.session_state.df_cust = None
if "tracked_order" not in st.session_state:
    st.session_state.tracked_order = None

# =====================================================
# 3. STYLES
# =====================================================
st.markdown("""
<style>
.header-style {font-size:26px; font-weight:bold; color:#1F618D;}
.info-box {padding:12px; background-color:#EBF5FB; border-radius:6px;}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 4. QR CODE FUNCTIONS
# =====================================================
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
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def decode_qr_code(uploaded_image):
    image = Image.open(uploaded_image).convert("RGB")
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(gray)
    return data if data else None

# =====================================================
# 5. DISTANCE FUNCTION
# =====================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

# =====================================================
# 6. SIDEBAR – DATA UPLOAD
# =====================================================
with st.sidebar:
    st.header("⚙️ System Setup")

    cust_file = st.file_uploader("Upload Customer.csv", type="csv")
    if cust_file:
        st.session_state.df_cust = pd.read_csv(cust_file)
        st.success("Customer data loaded")

    st.caption("BSD3513 Group Project")

if st.session_state.df_cust is None:
    st.warning("Please upload Customer.csv to continue")
    st.stop()

df = st.session_state.df_cust

# =====================================================
# 7. TABS
# =====================================================
tab1, tab2 = st.tabs(
    ["🛒 Buy & Track", "🗺️ Delivery Route (Pahang Hub)"]
)

# =====================================================
# TAB 1 – BUY & TRACK
# =====================================================
with tab1:
    st.markdown('<p class="header-style">Customer Portal</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # ---- BUY ----
    with col1:
        st.markdown('<div class="info-box"><b>Step 1: Purchase</b></div>', unsafe_allow_html=True)

        options = df["Order ID"].astype(str) + " | " + df["Customer Name"]
        selected = st.selectbox("Select Order", options)

        if st.button("Generate QR Code"):
            order_id = selected.split(" | ")[0]
            qr_img = generate_qr_code(order_id)

            st.image(qr_img, caption=f"Tracking ID: {order_id}")
            st.download_button(
                "Download QR Code",
                qr_img,
                file_name=f"{order_id}_QR.png",
                mime="image/png"
            )

    # ---- TRACK ----
    with col2:
        st.markdown('<div class="info-box"><b>Step 2: Track Order</b></div>', unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload QR Code", type=["png", "jpg"])

        if uploaded:
            scanned = decode_qr_code(uploaded)

            if scanned:
                record = df[df["Order ID"].astype(str) == scanned]

                if not record.empty:
                    st.success(f"Order Found: {scanned}")
                    st.session_state.tracked_order = record.iloc[0]

                    st.write(f"Customer: {record.iloc[0]['Customer Name']}")
                    st.write(f"City: {record.iloc[0]['City']}")
                    st.write(f"State: {record.iloc[0]['State']}")
                else:
                    st.error("Order not found")
            else:
                st.error("Invalid QR Code")

# =====================================================
# TAB 2 – ROUTE (PAHANG HUB ONLY)
# =====================================================
with tab2:
    st.markdown('<p class="header-style">Delivery Route (Pahang Only)</p>', unsafe_allow_html=True)

    order = st.session_state.tracked_order
    if order is None:
        st.info("Please track an order first")
        st.stop()

    # --- FIXED PAHANG LOCATIONS ---
    PORT_LAT, PORT_LON = 3.9767, 103.4242      # Port Kuantan
    HUB_LAT, HUB_LON = 3.8168, 103.3317        # Kuantan Hub (PAHANG)

    # Simulated customer home (offset near hub)
    HOME_LAT = HUB_LAT + 0.12
    HOME_LON = HUB_LON + 0.12

    # --- DISTANCES ---
    d1 = haversine(PORT_LAT, PORT_LON, HUB_LAT, HUB_LON)
    d2 = haversine(HUB_LAT, HUB_LON, HOME_LAT, HOME_LON)

    t1 = d1 / 80
    t2 = d2 / 60
    total_time = t1 + t2

    # --- MAP ---
    m = folium.Map(location=[HUB_LAT, HUB_LON], zoom_start=8)

    folium.Marker(
        [PORT_LAT, PORT_LON],
        popup="🚢 Port Kuantan",
        icon=folium.Icon(color="blue", icon="ship", prefix="fa")
    ).add_to(m)

    folium.Marker(
        [HUB_LAT, HUB_LON],
        popup="🏭 Kuantan Hub (Pahang)",
        icon=folium.Icon(color="green", icon="warehouse", prefix="fa")
    ).add_to(m)

    folium.Marker(
        [HOME_LAT, HOME_LON],
        popup=f"🏠 {order['City']}",
        icon=folium.Icon(color="red", icon="home", prefix="fa")
    ).add_to(m)

    folium.PolyLine(
        [(PORT_LAT, PORT_LON), (HUB_LAT, HUB_LON)],
        color="blue",
        tooltip=f"Port → Hub ({t1:.2f} hrs)"
    ).add_to(m)

    folium.PolyLine(
        [(HUB_LAT, HUB_LON), (HOME_LAT, HOME_LON)],
        color="green",
        tooltip=f"Hub → Home ({t2:.2f} hrs)"
    ).add_to(m)

    st_folium(m, width=900, height=500)

    st.metric("Estimated Delivery Time", f"{total_time:.2f} hours")
