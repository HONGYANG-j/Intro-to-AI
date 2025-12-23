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
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="SmartTrack Logistics",
    layout="wide",
    page_icon="📦"
)

# ==========================================
# SESSION STATE
# ==========================================
if "df" not in st.session_state:
    st.session_state.df = None
if "tracked_order" not in st.session_state:
    st.session_state.tracked_order = None

# ==========================================
# STYLES
# ==========================================
st.markdown("""
<style>
.header {font-size:26px; font-weight:bold; color:#2E86C1;}
.box {padding:12px; background:#D6EAF8; border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# QR FUNCTIONS
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
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def decode_qr(uploaded):
    image = Image.open(uploaded).convert("RGB")
    img = np.array(image)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    return data.strip() if data else None

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ Upload Dataset")
    file = st.file_uploader("Upload Customer.csv", type="csv")
    if file:
        st.session_state.df = pd.read_csv(file)
        st.success("Customer data loaded")

if st.session_state.df is None:
    st.warning("Please upload Customer.csv")
    st.stop()

df = st.session_state.df

# ==========================================
# TABS
# ==========================================
tab1, tab2 = st.tabs(["🛒 Buy & Track", "📍 Logistics Route"])

# ==========================================
# TAB 1 — BUY & TRACK
# ==========================================
with tab1:
    st.markdown('<p class="header">Customer Portal</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="box"><b>Step 1: Select Order</b></div>', unsafe_allow_html=True)
        options = df["Order ID"].astype(str) + " | " + df["Customer Name"]
        selected = st.selectbox("Order", options)

        if st.button("Generate QR"):
            order_id = selected.split(" | ")[0]
            qr = generate_qr_code(order_id)
            st.image(qr, caption=f"Tracking ID: {order_id}")
            st.download_button("Download QR", qr, f"{order_id}.png")

    with col2:
        st.markdown('<div class="box"><b>Step 2: Track Order</b></div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload QR", type=["png", "jpg"])

        if uploaded:
            scanned = decode_qr(uploaded)
            if scanned:
                record = df[df["Order ID"].astype(str) == scanned]
                if not record.empty:
                    st.session_state.tracked_order = record.iloc[0]
                    st.success(f"Order {scanned} found")
                else:
                    st.error("Order not found")
            else:
                st.error("Invalid QR")

# ==========================================
# TAB 2 — STATIC ROUTE (NETWORKX)
# ==========================================
with tab2:
    st.markdown('<p class="header">Static Logistics Route</p>', unsafe_allow_html=True)

    order = st.session_state.tracked_order
    if order is None:
        st.info("Track an order first.")
        st.stop()

    # Nodes
    port = "🚢 Port Kuantan\n(3.9767, 103.4242)"
    hub = "🏭 Kuantan Hub"
    home = f"🏠 {order['City']}"

    # Graph
    G = nx.DiGraph()
    G.add_edge(port, hub, weight=4.5)
    G.add_edge(hub, home, weight=2.0)

    pos = {
        port: (0, 2),
        hub: (0, 1),
        home: (0, 0)
    }

    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw(
        G, pos,
        with_labels=True,
        node_size=3000,
        node_color="#AED6F1",
        font_weight="bold",
        ax=ax
    )

    labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    ax.set_title(f"Delivery Route — Order {order['Order ID']}")
    ax.axis("off")

    st.pyplot(fig)

    st.metric(
        "⏱️ Estimated Delivery Time",
        f"{sum(labels.values())} Hours"
    )
