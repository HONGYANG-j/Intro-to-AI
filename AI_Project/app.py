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
st.set_page_config(page_title="SmartTrack Logistics", layout="wide", page_icon="📦")

# Initialize session state for data persistence
if 'df_cust' not in st.session_state:
    st.session_state['df_cust'] = None
if 'df_post' not in st.session_state:
    st.session_state['df_post'] = None
if 'tracked_order' not in st.session_state:
    st.session_state['tracked_order'] = None

# Custom CSS
st.markdown("""
<style>
    .header-style {font-size:24px; font-weight:bold; color:#2E86C1;}
    .success-box {padding:10px; background-color:#D4EFDF; border-radius:5px; color:#186A3B;}
    .info-box {padding:10px; background-color:#D6EAF8; border-radius:5px; color:#21618C;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SIDEBAR: SYSTEM SETUP (UPLOAD DATASETS)
# ==========================================
with st.sidebar:
    st.header("⚙️ 1. System Setup")
    st.info("Upload the required databases to start the system.")
    
    # Dataset 1: Customer Database
    cust_file = st.file_uploader("Upload 'Customer.csv'", type=['csv'])
    if cust_file:
        try:
            st.session_state['df_cust'] = pd.read_csv(cust_file)
            st.success("✅ Customer DB Loaded")
        except Exception as e:
            st.error(f"Error loading CSV: {e}")

    # Dataset 2: Postcode Database
    post_file = st.file_uploader("Upload 'Malaysia_Postcode...csv'", type=['csv'])
    if post_file:
        try:
            st.session_state['df_post'] = pd.read_csv(post_file)
            st.success("✅ Postcode DB Loaded")
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            
    st.divider()
    st.caption("Group Project BSD3513")

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def generate_barcode_img(text_data):
    """Generates a barcode image in memory."""
    code128 = barcode.get_barcode_class('code128')
    rv = io.BytesIO()
    code128(text_data, writer=ImageWriter()).write(rv)
    return rv

def decode_opencv(uploaded_image):
    """Decodes barcode using OpenCV."""
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    bardet = cv2.barcode_BarcodeDetector()
    retval, decoded_info, decoded_type, points = bardet.detectAndDecode(img)
    return decoded_info[0] if retval else None

def determine_hub(region):
    """Assigns a hub based on region."""
    if pd.isna(region): return "General Hub (KL)"
    region = region.strip()
    if region == 'Central': return "Central Hub (Shah Alam)"
    if region == 'North': return "Northern Hub (Ipoh)"
    if region == 'South': return "Southern Hub (Johor Bahru)"
    if region == 'East': return "East Coast Hub (Kuantan)"
    return "International Hub (KLIA)"

# ==========================================
# 3. MAIN INTERFACE
# ==========================================

# Check if data is loaded
if st.session_state['df_cust'] is None or st.session_state['df_post'] is None:
    st.warning("⚠️ Please upload BOTH datasets in the sidebar to proceed.")
    st.stop() # Stop execution here until files are uploaded

# Main Tabs
tab1, tab2 = st.tabs(["🛒 Page 1: Buy & Track", "🌳 Page 2: Logistics Tree Diagram"])

# --- TAB 1: CUSTOMER PORTAL (Buy & Track) ---
with tab1:
    st.markdown('<p class="header-style">Customer Portal</p>', unsafe_allow_html=True)
    
    col_buy, col_track = st.columns(2)
    
    # (a) BUY & GENERATE BARCODE
    with col_buy:
        st.markdown('<div class="info-box">🛒 <b>Step A: Buy Item</b></div>', unsafe_allow_html=True)
        st.write("Simulate a purchase to generate a tracking code.")
        
        df = st.session_state['df_cust']
        # Dropdown to pick an order
        options = df['Order ID'] + " | " + df['Customer Name']
        selected_option = st.selectbox("Choose an Order:", options.head(50)) # Limit to 50 for speed
        
        if st.button("Confirm Purchase"):
            order_id = selected_option.split(" | ")[0]
            
            # Generate Barcode
            img_data = generate_barcode_img(order_id)
            st.image(img_data, caption=f"Tracking ID: {order_id}")
            
            # Download
            st.download_button("📥 Download Barcode", img_data, f"{order_id}.png", "image/png")
    
    # (b) UPLOAD & TRACK STATUS
    with col_track:
        st.markdown('<div class="info-box">🔍 <b>Step B: Track Status</b></div>', unsafe_allow_html=True)
        st.write("Upload your barcode to check delivery status.")
        
        track_file = st.file_uploader("Upload Barcode Image", type=['png', 'jpg', 'jpeg'], key="tracker")
        
        if track_file:
            scanned_code = decode_opencv(track_file)
            
            if scanned_code:
                st.success(f"✅ Code Scanned: {scanned_code}")
                
                # Find Order in DB
                record = df[df['Order ID'] == scanned_code]
                
                if not record.empty:
                    data = record.iloc[0]
                    st.session_state['tracked_order'] = data # Save for Page 2
                    
                    st.write(f"**Status:** 🚚 Delivering")
                    st.write(f"**Customer:** {data['Customer Name']}")
                    st.write(f"**Destination:** {data['City']}, {data['State']}")
                    st.info("👉 Check 'Page 2' tab for the delivery route tree!")
                else:
                    st.error("❌ Order ID not found in database.")
            else:
                st.warning("⚠️ Could not read barcode.")

# --- TAB 2: LOGISTICS TREE DIAGRAM (c) & (d) ---
with tab2:
    st.markdown('<p class="header-style">Logistics Route Visualization</p>', unsafe_allow_html=True)
    
    order_data = st.session_state['tracked_order']
    
    if order_data is not None:
        # Define Nodes for (c) Tree Diagram
        node_A = "Port Klang (Start)"
        node_B = determine_hub(order_data['Region']) # Regional Hub
        node_C = f"{order_data['State']} Dist. Center"
        node_D = f"Home: {order_data['City']}"
        
        # Build Directed Graph
        G = nx.DiGraph()
        
        # Define Weights (Estimated Time in Hours)
        t1, t2, t3 = 4.5, 2.0, 1.0 # Static estimates for demo
        
        G.add_edge(node_A, node_B, weight=t1)
        G.add_edge(node_B, node_C, weight=t2)
        G.add_edge(node_C, node_D, weight=t3)
        
        # Layout & Drawing
        pos = {
            node_A: (0, 4),
            node_B: (0, 3),
            node_C: (0, 2),
            node_D: (0, 1)
        }
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Draw Tree
        nx.draw_networkx_nodes(G, pos, node_size=2500, node_color='#AED6F1', node_shape='s', ax=ax)
        nx.draw_networkx_edges(G, pos, width=2, edge_color='#2874A6', arrowsize=20, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", ax=ax)
        
        # Draw Edge Labels (Time)
        edge_labels = {
            (node_A, node_B): f"{t1} Hrs",
            (node_B, node_C): f"{t2} Hrs",
            (node_C, node_D): f"{t3} Hrs"
        }
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', ax=ax)
        
        ax.set_title(f"Delivery Path for Order #{order_data['Order ID']}")
        ax.axis('off')
        st.pyplot(fig)
        
        # (d) ESTIMATION DISPLAY
        st.divider()
        total_time = t1 + t2 + t3
        st.metric(label="⏱️ Total Estimated Arrival Time", value=f"{total_time} Hours")
        
        # Postcode Validation (Bonus Check)
        pc_df = st.session_state['df_post']
        if pd.notna(order_data['Postal Code']):
            # Clean and check postcode
            try:
                code_to_check = int(order_data['Postal Code'])
                # Assuming Postcode is in the 1st column of the helper CSV
                valid = pc_df[pc_df.iloc[:, 0] == code_to_check]
                if not valid.empty:
                    st.caption("✅ Verified via Malaysia Postcode Database")
                else:
                    st.caption("ℹ️ Standard routing applied (Postcode not in local DB)")
            except:
                pass
                
    else:
        st.info("ℹ️ No active order. Please go to 'Page 1', scan a barcode, and verify an order first.")
