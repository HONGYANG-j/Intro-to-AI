import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import barcode
from barcode.writer import ImageWriter
import io

# ==========================================
# 0. PAGE CONFIGURATION & SESSION SETUP
# ==========================================
st.set_page_config(page_title="SmartTrack Logistics", layout="wide", page_icon="📦")

# Initialize session state
if 'df_cust' not in st.session_state:
    st.session_state['df_cust'] = None
if 'df_post' not in st.session_state:
    st.session_state['df_post'] = None
if 'tracked_order' not in st.session_state:
    st.session_state['tracked_order'] = None

st.markdown("""
<style>
    .header-style {font-size:24px; font-weight:bold; color:#2E86C1;}
    .success-box {padding:10px; background-color:#D4EFDF; border-radius:5px; color:#186A3B;}
    .info-box {padding:10px; background-color:#D6EAF8; border-radius:5px; color:#21618C;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SIDEBAR: SYSTEM SETUP
# ==========================================
with st.sidebar:
    st.header("⚙️ 1. System Setup")
    st.info("Upload the required databases to start.")
    
    cust_file = st.file_uploader("Upload 'Customer.csv'", type=['csv'])
    if cust_file:
        try:
            st.session_state['df_cust'] = pd.read_csv(cust_file)
            st.success("✅ Customer DB Loaded")
        except Exception as e:
            st.error(f"Error: {e}")

    post_file = st.file_uploader("Upload 'Malaysia_Postcode...csv'", type=['csv'])
    if post_file:
        try:
            st.session_state['df_post'] = pd.read_csv(post_file)
            st.success("✅ Postcode DB Loaded")
        except Exception as e:
            st.error(f"Error: {e}")
            
    st.divider()
    st.caption("Group Project BSD3513")

# ==========================================
# 2. HELPER FUNCTIONS (HIGH RES & SHARPENING)
# ==========================================

def generate_barcode_img(text_data):
    """Generates a FAT, HIGH-CONTRAST barcode."""
    code128 = barcode.get_barcode_class('code128')
    rv = io.BytesIO()
    
    # CRITICAL FIX: module_width=0.5 makes bars thicker. quiet_zone=20 adds white space.
    options = {
        "module_width": 0.5, 
        "module_height": 15, 
        "quiet_zone": 20, 
        "background": "white", 
        "foreground": "black"
    }
    
    code128(text_data, writer=ImageWriter()).write(rv, options=options)
    return rv

def safe_detect(detector, img):
    """Helper to safely handle OpenCV return values (3 vs 4 items)."""
    result = detector.detectAndDecode(img)
    
    retval = False
    decoded_info = []
    
    if isinstance(result, tuple):
        if len(result) == 4:
            retval, decoded_info, decoded_type, points = result
        elif len(result) == 3:
            retval, decoded_info, points = result
    
    if retval and decoded_info:
        # Filter out empty strings
        valid_codes = [x for x in decoded_info if x]
        if valid_codes:
            return valid_codes[0]
    return None

def decode_opencv_robust(uploaded_image):
    """
    Decodes with Sharpening and Contrast enhancement.
    """
    # 1. Load with PIL to fix transparency
    image = Image.open(uploaded_image)
    
    # 2. Force White Background
    if image.mode in ('RGBA', 'LA'):
        background = Image.new(image.mode[:-1], image.size, (255, 255, 255))
        background.paste(image, image.split()[-1])
        image = background
    image = image.convert('RGB')
    
    # 3. Convert to OpenCV
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    detector = cv2.barcode_BarcodeDetector()
    
    # --- Attempt 1: Raw Image ---
    code = safe_detect(detector, img)
    if code: return code
    
    # --- Attempt 2: Grayscale ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    code = safe_detect(detector, gray)
    if code: return code
    
    # --- Attempt 3: Sharpening (New!) ---
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    code = safe_detect(detector, sharpened)
    if code: return code
    
    # --- Attempt 4: Binary Threshold (Extreme Contrast) ---
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    code = safe_detect(detector, thresh)
    if code: return code
    
    # --- Attempt 5: Zoom In (2x) ---
    zoomed = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    code = safe_detect(detector, zoomed)
    if code: return code

    return None

def determine_hub(region):
    if pd.isna(region): return "General Hub (KL)"
    region = str(region).strip()
    if region == 'Central': return "Central Hub (Shah Alam)"
    if region == 'North': return "Northern Hub (Ipoh)"
    if region == 'South': return "Southern Hub (Johor Bahru)"
    if region == 'East': return "East Coast Hub (Kuantan)"
    return "International Hub (KLIA)"

# ==========================================
# 3. MAIN INTERFACE
# ==========================================

if st.session_state['df_cust'] is None or st.session_state['df_post'] is None:
    st.warning("⚠️ Please upload BOTH datasets in the sidebar first.")
    st.stop()

tab1, tab2 = st.tabs(["🛒 Page 1: Buy & Track", "🌳 Page 2: Logistics Tree Diagram"])

# --- TAB 1 ---
with tab1:
    st.markdown('<p class="header-style">Customer Portal</p>', unsafe_allow_html=True)
    col_buy, col_track = st.columns(2)
    
    with col_buy:
        st.markdown('<div class="info-box">🛒 <b>Step A: Buy Item</b></div>', unsafe_allow_html=True)
        df = st.session_state['df_cust']
        options = df['Order ID'].astype(str) + " | " + df['Customer Name'].astype(str)
        selected_option = st.selectbox("Choose an Order:", options.head(50))
        
        if st.button("Confirm Purchase"):
            order_id = selected_option.split(" | ")[0]
            # Use new FAT barcode generator
            img_data = generate_barcode_img(order_id)
            st.image(img_data, caption=f"Tracking ID: {order_id} (High Res)")
            st.download_button("📥 Download Barcode", img_data, f"{order_id}.png", "image/png")
    
    with col_track:
        st.markdown('<div class="info-box">🔍 <b>Step B: Track Status</b></div>', unsafe_allow_html=True)
        track_file = st.file_uploader("Upload Barcode Image", type=['png', 'jpg', 'jpeg'], key="tracker")
        
        if track_file:
            scanned_code = decode_opencv_robust(track_file)
            
            if scanned_code:
                st.success(f"✅ Code Scanned: {scanned_code}")
                record = df[df['Order ID'] == scanned_code]
                if not record.empty:
                    data = record.iloc[0]
                    st.session_state['tracked_order'] = data
                    st.write(f"**Status:** 🚚 Delivering")
                    st.write(f"**Customer:** {data['Customer Name']}")
                    st.write(f"**Destination:** {data['City']}, {data['State']}")
                    st.info("👉 Check 'Page 2' tab for the route!")
                else:
                    st.error("❌ ID not found in database.")
            else:
                st.warning("⚠️ Still reading... Try downloading the barcode again (it is now generated larger).")

# --- TAB 2 ---
with tab2:
    st.markdown('<p class="header-style">Logistics Route Visualization</p>', unsafe_allow_html=True)
    order_data = st.session_state['tracked_order']
    
    if order_data is not None:
        node_A = "Port Klang (Start)"
        node_B = determine_hub(order_data['Region'])
        node_C = f"{order_data['State']} Dist. Center"
        node_D = f"Home: {order_data['City']}"
        
        G = nx.DiGraph()
        t1, t2, t3 = 4.5, 2.0, 1.0
        G.add_edge(node_A, node_B, weight=t1)
        G.add_edge(node_B, node_C, weight=t2)
        G.add_edge(node_C, node_D, weight=t3)
        
        pos = {node_A: (0, 4), node_B: (0, 3), node_C: (0, 2), node_D: (0, 1)}
        
        fig, ax = plt.subplots(figsize=(8, 6))
        nx.draw_networkx_nodes(G, pos, node_size=2500, node_color='#AED6F1', node_shape='s', ax=ax)
        nx.draw_networkx_edges(G, pos, width=2, edge_color='#2874A6', arrowsize=20, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", ax=ax)
        
        edge_labels = {
            (node_A, node_B): f"{t1} Hrs",
            (node_B, node_C): f"{t2} Hrs",
            (node_C, node_D): f"{t3} Hrs"
        }
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', ax=ax)
        
        ax.set_title(f"Delivery Path for Order #{order_data['Order ID']}")
        ax.axis('off')
        st.pyplot(fig)
        
        st.divider()
        st.metric(label="⏱️ Total Estimated Arrival Time", value=f"{t1 + t2 + t3} Hours")
        
    else:
        st.info("ℹ️ No active order. Scan a barcode in Page 1 first.")
