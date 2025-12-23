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
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. QR CODE FUNCTIONS
# ==========================================

def generate_qr_code(text):
    """Generate high-quality QR code"""
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
    """Decode QR code safely using OpenCV"""
    try:
        image = Image.open(uploaded_image).convert("RGB")
    except:
        return None

    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)

    if data:
        return data.strip()
    return None


def determine_hub(region):
    if pd.isna(region):
        return "General Hub (KL)"
    region = region.strip()
    if region == "Central":
        return "Central Hub (Shah Alam)"
    if region == "North":
        return "Northern Hub (Ipoh)"
    if region == "South":
        return "Southern Hub (Johor Bahru)"
    if region == "East":
        return "East Coast Hub (Kuantan)"
    return "International Hub (KLIA)"

# ==========================================
# 3. SIDEBAR – DATA UPLOAD
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

if st.session_state.df_cust is None or st.session_state.df_post is None:
    st.warning("Please upload BOTH datasets to continue.")
    st.stop()

df = st.session_state.df_cust

# ==========================================
# 4. MAIN TABS
# ==========================================
tab1, tab2 = st.tabs(
    ["🛒 Page 1: Buy & Track", "🌳 Page 2: Logistics Route"]
)

# ==========================================
# TAB 1 – BUY & TRACK
# ==========================================
with tab1:
    st.markdown(
        '<p class="header-style">Customer Portal</p>',
        unsafe_allow_html=True
    )

    col_buy, col_track = st.columns(2)

    # ---- BUY ITEM ----
    with col_buy:
        st.markdown(
            '<div class="info-box"><b>Step A: Buy Item</b></div>',
            unsafe_allow_html=True
        )

        options = (
            df["Order ID"].astype(str)
            + " | "
            + df["Customer Name"].astype(str)
        )

        selected = st.selectbox("Choose an Order", options)

        if st.button("Confirm Purchase"):
            order_id = selected.split(" | ")[0]
            qr_img = generate_qr_code(order_id)

            st.image(qr_img, caption=f"Tracking ID: {order_id}")
            st.download_button(
                "📥 Download QR Code",
                qr_img,
                file_name=f"{order_id}_QR.png",
                mime="image/png"
            )

    # ---- TRACK ITEM ----
    with col_track:
        st.markdown(
            '<div class="info-box"><b>Step B: Track Order</b></div>',
            unsafe_allow_html=True
        )

        uploaded = st.file_uploader(
            "Upload QR Code Image",
            type=["png", "jpg", "jpeg"]
        )

        if uploaded:
            st.image(uploaded, caption="Uploaded QR Code")
            scanned = decode_qr_code(uploaded)

            if scanned:
                st.success(f"✅ Order ID Scanned: {scanned}")

                record = df[df["Order ID"].astype(str) == scanned]
                if not record.empty:
                    data = record.iloc[0]
                    st.session_state.tracked_order = data

                    st.write(f"**Customer:** {data['Customer Name']}")
                    st.write(
                        f"**Destination:** {data['City']}, {data['State']}"
                    )
                    st.info(
                        "👉 Go to Page 2 to view the delivery route"
                    )
                else:
                    st.error("❌ Order ID not found in database")
            else:
                st.error("⚠️ QR code not detected. Please upload the original file.")

# ==========================================
# TAB 2 – LOGISTICS ROUTE
# ==========================================
PORT = ("Port Kuantan", 3.9767, 103.4242)
HUBS = ("Kuantan Hub", 3.8168, 103.3317)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius (km)
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius (km)
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))


with tab2:
    st.markdown(
        '<p class="header-style">Logistics Route Visualization</p>',
        unsafe_allow_html=True
    )

    order = st.session_state.tracked_order
    if order is None:
        st.info("Scan a QR code in Page 1 first.")
        st.stop()

    # --- COORDINATES ---
    port_name, port_lat, port_lon = PORT

    hub_name, hub_lat, hub_lon = HUBS.get(
        order["Region"],
        ("Kuantan Hub", 3.8168, 103.3317)
    )

    # Home location (example – replace later with dataset lat/lon)
    home_lat, home_lon = hub_lat + 0.15, hub_lon + 0.15

    # --- DISTANCES ---
    d1 = haversine(port_lat, port_lon, hub_lat, hub_lon)
    d2 = haversine(hub_lat, hub_lon, home_lat, home_lon)

    t1 = d1 / 80   # hours
    t2 = d2 / 60

    total_time = t1 + t2

    # --- MAP ---
    m = folium.Map(location=[hub_lat, hub_lon], zoom_start=7)

    # Markers
    folium.Marker(
        [port_lat, port_lon],
        popup="🚢 Port Kuantan",
        icon=folium.Icon(color="blue", icon="ship", prefix="fa")
    ).add_to(m)

    folium.Marker(
        [hub_lat, hub_lon],
        popup=f"🏭 {hub_name}",
        icon=folium.Icon(color="green", icon="warehouse", prefix="fa")
    ).add_to(m)

    folium.Marker(
        [home_lat, home_lon],
        popup=f"🏠 {order['City']}",
        icon=folium.Icon(color="red", icon="home", prefix="fa")
    ).add_to(m)

    # Routes
    folium.PolyLine(
        [(port_lat, port_lon), (hub_lat, hub_lon)],
        tooltip=f"Port → Hub ({t1:.2f} hrs)",
        color="blue"
    ).add_to(m)

    folium.PolyLine(
        [(hub_lat, hub_lon), (home_lat, home_lon)],
        tooltip=f"Hub → Home ({t2:.2f} hrs)",
        color="green"
    ).add_to(m)

    # 🚚 Vehicle icon (at hub for now)
    folium.Marker(
        [hub_lat, hub_lon],
        icon=folium.CustomIcon(
            "https://cdn-icons-png.flaticon.com/512/1995/1995470.png",
            icon_size=(40, 40)
        )
    ).add_to(m)

    st_folium(m, width=900, height=500)

    st.metric(
        "⏱️ Estimated Delivery Time",
        f"{total_time:.2f} hours"
    )

