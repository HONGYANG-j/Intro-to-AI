import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode
import barcode
from barcode.writer import ImageWriter
import io

# ==========================================
# 0. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="SmartTrack Logistics", layout="wide", page_icon="📦")

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {font-size:32px; font-weight:bold; color:#1E88E5;}
    .status-box {padding:15px; border-radius:10px; color:white; font-weight:bold; text-align:center;}
    .delivering {background-color: #28B463;} /* Green */
    .processing {background-color: #F1C40F; color:black;} /* Yellow */
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATA LOADING MODULE
# ==========================================
@st.cache_data
def load_data():
    # Load Main Customer Data
    try:
        df_cust = pd.read_csv("Customer.csv")
        # Load Helper Postcode Data
        df_post = pd.read_csv("Malaysia_Postcode-postcodes.csv")
        return df_cust, df_post
    except FileNotFoundError:
        st.error("❌ Database files not found. Please upload 'Customer.csv' and 'Malaysia_Postcode-postcodes.csv'.")
        return None, None

df_customers, df_postcodes = load_data()

# ==========================================
# 2. HELPER FUNCTIONS (Barcode & Vision)
# ==========================================

def generate_barcode_image(order_id):
    """Generates a barcode image in memory for the user to download."""
    code128 = barcode.get_barcode_class('code128')
    rv = io.BytesIO()
    code128(order_id, writer=ImageWriter()).write(rv)
    return rv

def scan_barcode_from_image(uploaded_image):
    """Decodes barcode from an uploaded image file using pyzbar/opencv."""
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    # Attempt decoding
    decoded_objects = decode(img)
    if decoded_objects:
        return decoded_objects[0].data.decode("utf-8")
    return None

def get_hub_from_region(region):
    """Simple logic to assign a Regional Hub based on dataset Region."""
    if region == 'Central': return "Central Hub (Shah Alam)"
    if region == 'North': return "Northern Hub (Ipoh)"
    if region == 'South': return "Southern Hub (Johor Bahru)"
    if region == 'East': return "East Coast Hub (Kuantan)"
    return "International Hub (KLIA)"

# ==========================================
# 3. GUI PAGE 1: CUSTOMER PORTAL
# ==========================================

st.markdown('<p class="main-header">📦 Smart Parcel System</p>', unsafe_allow_html=True)

# We use tabs to separate the "Purchase" phase from the "Tracking" phase on Page 1
tab_buy, tab_track = st.tabs(["🛒 Step 1: Buy & Generate Barcode", "🔍 Step 2: Track Parcel"])

with tab_buy:
    st.subheader("(a) Customer Purchase Simulation")
    st.info("Select a customer order to simulate a purchase. This will generate your unique tracking barcode.")
    
    if df_customers is not None:
        # User selects an order
        sample_orders = df_customers.sample(20) # Limit to 20 for dropdown speed
        selected_order_row = st.selectbox(
            "Select Your Order:", 
            sample_orders['Order ID'] + " - " + sample_orders['Customer Name']
        )
        
        if st.button("🛒 Buy & Generate Barcode"):
            order_id = selected_order_row.split(" - ")[0]
            
            # Generate Barcode
            img_data = generate_barcode_image(order_id)
            st.image(img_data, caption=f"Barcode for {order_id}", width=400)
            
            # Download Button
            st.download_button(
                label="📥 Download Barcode",
                data=img_data,
                file_name=f"barcode_{order_id}.png",
                mime="image/png"
            )
            st.success(f"Purchase Confirmed! Save this barcode to track your package.")

with tab_track:
    st.subheader("(b) Check Parcel Status")
    st.write("Upload your barcode to see where your parcel is.")
    
    uploaded_file = st.file_uploader("Upload Barcode Image", type=['png', 'jpg', 'jpeg'])
    
    if 'track_status' not in st.session_state:
        st.session_state['track_status'] = None
        st.session_state['order_details'] = None

    if uploaded_file:
        scanned_id = scan_barcode_from_image(uploaded_file)
        
        if scanned_id:
            st.success(f"✅ Barcode Detected: {scanned_id}")
            
            # Search in Database
            order_match = df_customers[df_customers['Order ID'] == scanned_id]
            
            if not order_match.empty:
                details = order_match.iloc[0]
                st.session_state['order_details'] = details
                st.session_state['track_status'] = "Delivering" # Simulating active status
                
                # Show Status UI
                st.markdown(f"""
                <div class="status-box delivering">
                    STATUS: DELIVERING<br>
                    Heading to: {details['City']}, {details['State']}
                </div>
                """, unsafe_allow_html=True)
                
                st.info("👉 Go to **Page 2 (Tree Diagram)** below to see the live delivery route!")
            else:
                st.error("❌ Order ID not found in system.")
        else:
            st.warning("⚠️ Could not read barcode. Please try a clearer image.")

st.markdown("---")

# ==========================================
# 4. GUI PAGE 2: ROUTING & TREE DIAGRAM
# ==========================================
st.subheader("(c) Delivery Path Visualization")

if st.session_state['track_status'] == "Delivering" and st.session_state['order_details'] is not None:
    details = st.session_state['order_details']
    
    # --- 4.1 BUILD TREE GRAPH ---
    # Nodes: A (Port) -> B (Regional Hub) -> C (State Center) -> D (Home)
    
    start_node = "Port Klang (Main Hub)"
    regional_node = get_hub_from_region(details.get('Region', 'Central'))
    state_node = f"{details['State']} Distribution Center"
    end_node = f"Home: {details['City']}\n({details['Customer Name']})"
    
    # Create Graph
    G = nx.DiGraph() # Directed Graph for Flow
    
    # Add Edges with 'Weights' (Time in hours)
    # Using simple logic: Farther regions = more time
    time_1 = 4.0 # Port to Region
    time_2 = 2.5 # Region to State
    time_3 = 1.0 # State to Home
    
    G.add_edge(start_node, regional_node, weight=time_1)
    G.add_edge(regional_node, state_node, weight=time_2)
    G.add_edge(state_node, end_node, weight=time_3)
    
    # --- 4.2 DRAW TREE DIAGRAM ---
    col_graph, col_info = st.columns([3, 1])
    
    with col_graph:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Tree Layout (Hierarchical)
        pos = {
            start_node: (0, 10),
            regional_node: (0, 7),
            state_node: (0, 4),
            end_node: (0, 1)
        }
        
        # Draw Nodes
        nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='#85C1E9', node_shape='s', ax=ax)
        # Draw Edges
        nx.draw_networkx_edges(G, pos, width=3, edge_color='#2E86C1', arrowstyle='->', arrowsize=20, ax=ax)
        # Draw Labels
        nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold', ax=ax)
        
        # Draw Edge Labels (Time)
        edge_labels = {
            (start_node, regional_node): f"{time_1} Hrs",
            (regional_node, state_node): f"{time_2} Hrs",
            (state_node, end_node): f"{time_3} Hrs"
        }
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', ax=ax)
        
        ax.set_title(f"Delivery Route for Order #{details['Order ID']}", fontsize=14)
        ax.axis('off')
        st.pyplot(fig)

    # --- 4.3 ESTIMATION (d) ---
    with col_info:
        st.markdown("### ⏱️ Estimation")
        total_time = time_1 + time_2 + time_3
        st.metric(label="Total Estimated Arrival", value=f"{total_time} Hours")
        
        st.write("**Path Details:**")
        st.write(f"1. 🚢 {start_node}")
        st.write("   ↓")
        st.write(f"2. 🏭 {regional_node}")
        st.write("   ↓")
        st.write(f"3. 🚚 {state_node}")
        st.write("   ↓")
        st.write(f"4. 🏠 {end_node}")
        
        # Validate with Helper Dataset (Postcode)
        # Check if the postcode exists in the helper file
        pc = int(details['Postal Code']) if pd.notnull(details['Postal Code']) else 0
        valid_zone = df_postcodes[df_postcodes.iloc[:, 0] == pc] # Assuming Col 0 is postcode
        
        if not valid_zone.empty:
            st.success("✅ Postcode Verified in Malaysia Database")
        else:
            st.caption(f"ℹ️ Postcode {pc} routed via standard maps.")

else:
    st.info("Waiting for barcode scan... Please track a parcel in Step 2 above.")

# ==========================================
# ESG FOOTER
# ==========================================
st.markdown("---")
st.caption("🌱 **ESG Note:** Optimized tree routing reduces unnecessary mileage between distribution centers, lowering carbon emissions.")
