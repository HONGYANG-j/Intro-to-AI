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
st.set_page_config(
    page_title="SmartTrack Logistics",
    layout="wide",
    page_icon="📦"
)

# =====================================================
# SESSION STATE
# =====================================================
for key in ["cust_df", "pc_df", "loc_df", "order", "verified"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "verified" else False

# =====================================================
# STYLES
# =====================================================
st.markdown("""
<style>
.header {font-size:26px; font-weight:bold; color:#1F618D;}
.box {padding:12px; background:#EBF5FB; border-radius:8px; margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

# =====================================================
# QR FUNCTIONS
# =====================================================
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

# =====================================================
# DISTANCE / ETA
# =====================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

# =====================================================
# SIDEBAR – DATA UPLOAD
# =====================================================
with st.sidebar:
    st.header("📂 Upload Required Data")

    cust = st.file_uploader("Customer.csv", type="csv")
    if cust:
        st.session_state.cust_df = pd.read_csv(cust)
        st.success("Customer data loaded")

    pc = st.file_uploader("Postcode.csv", type=["csv", "txt"])
    if pc:
        st.session_state.pc_df = pd.read_csv(pc, header=None,
                                             names=["Postcode", "Area", "City", "State"])
        st.success("Postcode data loaded")

    loc = st.file_uploader("Latitude_Longitude.csv", type="csv")
    if loc:
        st.session_state.loc_df = pd.read_csv(loc)
        st.success("Location data loaded")

# =====================================================
# VALIDATION (FIXED)
# =====================================================
if (
    st.session_state.cust_df is None
    or st.session_state.pc_df is None
    or st.session_state.loc_df is None
):
    st.warning("📌 Please upload ALL 3 CSV files to continue.")
    st.stop()

cust_df = st.session_state.cust_df
pc_df = st.session_state.pc_df
loc_df = st.session_state.loc_df

# =====================================================
# TABS
# =====================================================
tab1, tab2 = st.tabs(["🛒 Buy & Track", "🚚 Tracking Progress"])

# =====================================================
# TAB 1 – BUY & VERIFY
# =====================================================
with tab1:
    st.markdown('<p class="header">Customer Portal</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="box">Step 1: Select Order</div>', unsafe_allow_html=True)
        choice = st.selectbox(
            "Choose Order",
            cust_df["Order ID"].astype(str) + " | " + cust_df["Customer Name"]
        )

        if st.button("Generate QR"):
            oid = choice.split(" | ")[0]
            qr = generate_qr(oid)
            st.image(qr)
            st.download_button("Download QR", qr, f"{oid}.png")

    with col2:
        st.markdown('<div class="box">Step 2: Upload QR Code</div>', unsafe_allow_html=True)
        upload = st.file_uploader("Upload QR", type=["png", "jpg"])

        if upload:
            result = decode_qr(upload)
            if result:
                rec = cust_df[cust_df["Order ID"].astype(str) == result]
                if not rec.empty:
                    st.session_state.order = rec.iloc[0]
                    st.session_state.verified = True
                    st.success("QR verified successfully ✅")
                else:
                    st.error("Order not found")
            else:
                st.error("Invalid QR code")

# =====================================================
# TAB 2 – TRACKING
# =====================================================
with tab2:
    st.markdown('<p class="header">Delivery Tracking</p>', unsafe_allow_html=True)

    if not st.session_state.verified:
        st.info("""
        📌 **How to Track**
        1. Go to Page 1  
        2. Upload & verify QR code  
        3. Return here to see delivery progress
        """)
        st.stop()

    order = st.session_state.order

    # -------------------------------------------------
    # LOCATION LOOKUP
    # -------------------------------------------------
    pc_row = pc_df[pc_df["Postcode"] == order["Postcode"]]
    area = pc_row.iloc[0]["Area"]

    loc_row = loc_df[loc_df["Area"] == area]
    home_lat = loc_row.iloc[0]["Latitude"]
    home_lon = loc_row.iloc[0]["Longitude"]

    # Fixed logistics points
    port = (3.9767, 103.4242)      # Port Kuantan
    hub = (3.8168, 103.3317)       # Kuantan Hub
    home = (home_lat, home_lon)

    # -------------------------------------------------
    # ETA CALCULATION
    # -------------------------------------------------
    d1 = haversine(*port, *hub)     # Truck
    d2 = haversine(*hub, *home)     # Last mile

    eta_hours = d1 / 70 + d2 / 40

    # -------------------------------------------------
    # STATUS STEPS (TAOBAO STYLE)
    # -------------------------------------------------
    steps = [
        "📦 Order Confirmed",
        "🚚 Picked Up from Port",
        "🏭 At Hub",
        "🛵 Out for Delivery",
        "✅ Delivered"
    ]

    current_step = 2  # simulate

    st.markdown("### 📍 Order Progress")

    for i, step in enumerate(steps):
        if i < current_step:
            st.markdown(f"✅ **{step}**")
        elif i == current_step:
            st.markdown(f"🔵 **{step}** _(Current)_")
        else:
            st.markdown(f"⚪ {step}")

    # -------------------------------------------------
    # INFO BOX
    # -------------------------------------------------
    st.markdown("---")
    st.info(f"""
    **Order ID:** {order['Order ID']}  
    **Customer:** {order['Customer Name']}  
    **Destination:** {area}, {order['State']}  
    **Home Coordinates:** ({home_lat:.5f}, {home_lon:.5f})  
    **Estimated Time Remaining:** ⏱ {eta_hours:.2f} hours  
    """)
