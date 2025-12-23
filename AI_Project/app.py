import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
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
    st.warning("Please upload Customer.csv to continue.")
    st.stop()

df = st.session_state.df_cust

# ==========================================
# 4. MAIN TABS
# ==========================================
tab1, tab2 = st.tabs(
    ["🛒 Page 1: Buy & Track", "📍 Page 2: Static Logistics Route"]
)

# ==========================================
# TAB 1 – BUY & TRACK
# ==========================================
with tab1:
    st.markdown('<p class="header-style">Customer Portal</p>', unsafe_allow_html=True)

    col_buy, col_track = st.columns(2)

    # ---- BUY ITEM ----
    with col_buy:
        st.markdown('<div class="info-box"><b>Step A: Buy Item</b></div>', unsafe_allow_html=True)

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
        st.markdown('<div class="info-box"><b>Step B: Track Order</b></div>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Upload QR Code Image",
            type=["png", "jpg", "jpeg"]
        )

        if uploaded:
            scanned = decode_qr_code(uploaded)
            if scanned:
                record = df[df["Order ID"].astype(str) == scanned]
                if not record.empty:
                    st.session_state.tracked_order = record.iloc[0]
                    st.success(f"✅ Order {scanned} Found")
                else:
                    st.error("❌ Order not found")
            else:
                st.error("⚠️ QR Code not detected")

# ==========================================
# TAB 2 – STATIC LOGISTICS ROUTE
# ==========================================
with tab2:
    st.markdown('<p class="header-style">📍 Static Logistics Route</p>', unsafe_allow_html=True)

    order = st.session_state.tracked_order
    if order is None:
        st.info("Scan a QR code in Page 1 first.")
        st.stop()

    # --- Nodes ---
    port = "🚢 Port Kuantan\n(3.9767°N, 103.4242°E)"
    hub = "🏭 Kuantan Hub"
    dc = f"📦 {order['State']} Distribution Center"
    home = f"🏠 Customer Home ({order['City']})"

    # --- Graph ---
    G = nx.DiGraph()
    G.add_edge(port, hub, weight=4.5)
    G.add_edge(hub, dc, weight=2.0)
    G.add_edge(dc, home, weight=1.0)

    pos = {
        port: (0, 3),
        hub: (0, 2),
        dc: (0, 1),
        home: (0, 0)
    }

    fig, ax = plt.subplots(figsize=(9, 6))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=3000,
        node_color="#AED6F1",
        font_weight="bold",
        ax=ax
    )

    labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax)

    ax.set_title(f"🚚 Delivery Route for Order {order['Order ID']}")
    ax.axis("off")

    st.pyplot(fig)

    total_time = sum(labels.values())
    st.metric("⏱️ Total Estimated Delivery Time", f"{total_time} Hours")
