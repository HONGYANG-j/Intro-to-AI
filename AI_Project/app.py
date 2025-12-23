import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import Image
import barcode
from barcode.writer import ImageWriter
import io

# ==========================================
# 0. PAGE CONFIGURATION & SESSION SETUP
# ==========================================
st.set_page_config(
    page_title="SmartTrack Logistics",
    layout="wide",
    page_icon="📦"
)

if 'df_cust' not in st.session_state:
    st.session_state['df_cust'] = None
if 'df_post' not in st.session_state:
    st.session_state['df_post'] = None
if 'tracked_order' not in st.session_state:
    st.session_state['tracked_order'] = None

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
# 2. BARCODE FUNCTIONS (FIXED & ROBUST)
# ==========================================

def generate_barcode_img(text_data):
    """Generate high-resolution barcode for reliable OpenCV scanning"""
    code128 = barcode.get_barcode_class('code128')
    buffer = io.BytesIO()

    options = {
        "module_width": 1.2,
        "module_height": 60,
        "quiet_zone": 30,
        "font_size": 0,
        "dpi": 300,
        "background": "white",
        "foreground": "black"
    }

    code128(text_data, writer=ImageWriter()).write(buffer, options=options)
    buffer.seek(0)
    return buffer


def decode_barcode(uploaded_image):
    """Reliable barcode decoding using OpenCV"""
    try:
        image = Image.open(uploaded_image).convert("L")
    except:
        return None

    img = np.array(image)

    # Binary threshold (important)
    _, img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)

    # Upscale image
    img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)

    detector = cv2.barcode_BarcodeDetector()
    ok, decoded_info, _, _ = detector.detectAndDecode(img)

    if ok and decoded_info:
        for code in decoded_info:
            if code.strip():
                return code.strip()

    return None


def determine_hub(region):
    if pd.isna(region):
        return "General Hub (KL)"
    region = region.strip()
    if region == 'Central':
        return "Central Hub (Shah Alam)"
    if region == 'North':
        return "Northern Hub (Ipoh)"
    if region == 'South':
        return "Southern Hub (Johor Bahru)"
    if region == 'East':
        return "East Coast Hub (Kuantan)"
    return "International Hub (KLIA)"

# ==========================================
# 3. SIDEBAR – DATA UPLOAD
# ==========================================
with st.sidebar:
    st.header("⚙️ System Setup")

    cust_file = st.file_uploader("Upload Customer.csv", type="csv")
    if cust_file:
        st.session_state['df_cust'] = pd.read_csv(cust_file)
        st.success("Customer database loaded")

    post_file = st.file_uploader("Upload Malaysia_Postcode.csv", type="csv")
    if post_file:
        st.session_state['df_post'] = pd.read_csv(post_file)
        st.success("Postcode database loaded")

    st.caption("Group Project BSD3513")

if st.session_state['df_cust'] is None or st.session_state['df_post'] is None:
    st.warning("Please upload BOTH datasets to continue.")
    st.stop()

df = st.session_state['df_cust']

# ==========================================
# 4. MAIN TABS
# ==========================================
tab1, tab2 = st.tabs(["🛒 Buy & Track", "🌳 Logistics Route"])

# ==========================================
# TAB 1 – BUY & TRACK
# ==========================================
with tab1:
    st.markdown('<p class="header-style">Customer Portal</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # ---- BUY ITEM ----
    with col1:
        st.markdown('<div class="info-box"><b>Step A: Buy Item</b></div>', unsafe_allow_html=True)

        options = df['Order ID'].astype(str) + " | " + df['Customer Name']
        selected = st.selectbox("Choose an Order", options)

        if st.button("Confirm Purchase"):
            order_id = selected.split(" | ")[0]
            barcode_img = generate_barcode_img(order_id)

            st.image(barcode_img, caption=f"Tracking ID: {order_id}")
            st.download_button(
                "Download Barcode",
                barcode_img,
                file_name=f"{order_id}.png",
                mime="image/png"
            )

    # ---- TRACK ITEM ----
    with col2:
        st.markdown('<div class="info-box"><b>Step B: Track Order</b></div>', unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload Barcode Image", type=['png', 'jpg'])

        if uploaded:
            st.image(uploaded, caption="Uploaded Barcode (Preview)")
            scanned = decode_barcode(uploaded)

            if scanned:
                st.success(f"Scanned Order ID: {scanned}")

                record = df[df['Order ID'].astype(str) == scanned]
                if not record.empty:
                    data = record.iloc[0]
                    st.session_state['tracked_order'] = data

                    st.write(f"Customer: {data['Customer Name']}")
                    st.write(f"Destination: {data['City']}, {data['State']}")
                    st.info("Go to Page 2 to view delivery route")
                else:
                    st.error("Order ID not found")
            else:
                st.error("Barcode unreadable. Please regenerate and upload original image.")

# ==========================================
# TAB 2 – LOGISTICS ROUTE
# ==========================================
with tab2:
    st.markdown('<p class="header-style">Logistics Route Visualization</p>', unsafe_allow_html=True)

    order = st.session_state['tracked_order']

    if order is None:
        st.info("Scan a barcode first on Page 1")
        st.stop()

    start = "Port Klang"
    hub = determine_hub(order['Region'])
    dc = f"{order['State']} Distribution Center"
    home = f"Customer Home ({order['City']})"

    G = nx.DiGraph()
    G.add_edge(start, hub, weight=4.5)
    G.add_edge(hub, dc, weight=2.0)
    G.add_edge(dc, home, weight=1.0)

    pos = {
        start: (0, 3),
        hub: (0, 2),
        dc: (0, 1),
        home: (0, 0)
    }

    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_size=2500,
            node_color="#AED6F1", font_weight="bold", ax=ax)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax)

    ax.set_title(f"Delivery Route for Order {order['Order ID']}")
    ax.axis("off")

    st.pyplot(fig)

    total_time = sum(labels.values())
    st.metric("Total Estimated Delivery Time", f"{total_time} Hours")
