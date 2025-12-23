import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import qrcode
import io
from PIL import Image
import time

# ==========================================
# 0. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="SmartTrack Logistics",
    layout="wide",
    page_icon="📦"
)

# ==========================================
# 1. SESSION STATE
# ==========================================
if "df_cust" not in st.session_state:
    st.session_state.df_cust = None
if "tracked_order" not in st.session_state:
    st.session_state.tracked_order = None

# ==========================================
# 2. STYLES
# ==========================================
st.markdown("""
<style>
.header-style {font-size:24px; font-weight:bold; color:#2E86C1;}
.info-box {padding:10px; background-color:#D6EAF8; border-radius:5px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. QR CODE FUNCTIONS
# ==========================================
def generate_qr_code(text):
    qr = qrcode.QRCode(version=2, box_size=8, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def decode_qr_code(uploaded_image):
    img = Image.open(uploaded_image)
    return img.info.get("text", None)

# ==========================================
# 4. SIDEBAR – DATA UPLOAD
# ==========================================
with st.sidebar:
    st.header("⚙️ System Setup")
    cust_file = st.file_uploader("Upload Customer.csv", type="csv")

    if cust_file:
        st.session_state.df_cust = pd.read_csv(cust_file)
        st.success("Customer database loaded")

if st.session_state.df_cust is None:
    st.warning("Please upload Customer.csv to continue.")
    st.stop()

df = st.session_state.df_cust

# ==========================================
# 5. MAIN TABS
# ==========================================
tab1, tab2 = st.tabs(
    ["🛒 Page 1: Buy & Track", "🗺️ Page 2: Live Logistics Map"]
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
            st.image(qr)
            st.download_button("Download QR", qr, f"{order_id}.png")

    with col2:
        st.markdown('<div class="info-box"><b>Step B: Track Order</b></div>', unsafe_allow_html=True)
        upload = st.file_uploader("Upload QR Code", type=["png", "jpg"])

        if upload:
            st.image(upload)
            scanned = Image.open(upload)
            order_id = selected.split(" | ")[0]
            record = df[df["Order ID"].astype(str) == order_id]

            if not record.empty:
                st.session_state.tracked_order = record.iloc[0]
                st.success(f"Order {order_id} tracked")
                st.info("Go to Page 2 to view route")

# ==========================================
# TAB 2 – LOGISTICS MAP (PAHANG ONLY)
# ==========================================
with tab2:
    st.markdown('<p class="header-style">Live Logistics Route (Pahang)</p>', unsafe_allow_html=True)

    order = st.session_state.tracked_order
    if order is None:
        st.info("Track an order first.")
        st.stop()

    # 📍 Coordinates
    PORT = ("Port Kuantan", 3.9767, 103.4242)
    HUB = ("Kuantan Hub", 3.8168, 103.3317)
    HOME = ("Customer", 3.7, 103.3)  # simulated Pahang delivery

    # Distance calculation
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        return 2 * R * asin(sqrt(a))

    d1 = haversine(PORT[1], PORT[2], HUB[1], HUB[2])
    d2 = haversine(HUB[1], HUB[2], HOME[1], HOME[2])
    eta = d1/80 + d2/60

    # 🗺️ Folium Map
    m = folium.Map(location=[HUB[1], HUB[2]], zoom_start=8)

    # Markers
    folium.Marker(
        [PORT[1], PORT[2]],
        popup="🚢 Port Kuantan",
        icon=folium.Icon(color="blue", icon="ship", prefix="fa")
    ).add_to(m)

    folium.Marker(
        [HUB[1], HUB[2]],
        popup="🏭 Kuantan Hub",
        icon=folium.Icon(color="green", icon="warehouse", prefix="fa")
    ).add_to(m)

    folium.Marker(
        [HOME[1], HOME[2]],
        popup="🏠 Customer",
        icon=folium.Icon(color="red", icon="home", prefix="fa")
    ).add_to(m)

    # Routes
    folium.PolyLine(
        [(PORT[1], PORT[2]), (HUB[1], HUB[2])],
        color="blue",
        tooltip="Port → Hub"
    ).add_to(m)

    folium.PolyLine(
        [(HUB[1], HUB[2]), (HOME[1], HOME[2])],
        color="green",
        tooltip="Hub → Customer"
    ).add_to(m)

    # 🚚 Vehicle icon
    folium.Marker(
        [HUB[1], HUB[2]],
        icon=folium.CustomIcon(
            "https://cdn-icons-png.flaticon.com/512/1995/1995470.png",
            icon_size=(40, 40)
        )
    ).add_to(m)

    st_folium(m, width=900, height=500)

    # ⏱ Dynamic ETA animation
    st.subheader("⏱ Live ETA Progress")
    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        progress.progress(i + 1)

    st.metric("Estimated Delivery Time", f"{eta:.2f} hours")
