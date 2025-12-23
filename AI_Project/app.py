import streamlit as st
import cv2
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pyzbar.pyzbar import decode
from PIL import Image

# ==========================================
# CONFIGURATION
# ==========================================
st.set_page_config(page_title="Smart Logistics AI", layout="wide", page_icon="🚚")

# Custom CSS for a professional look
st.markdown("""
<style>
    .main-header {font-size:36px; font-weight:bold; color:#2E86C1;}
    .metric-box {background-color:#F0F2F6; padding:15px; border-radius:10px; border-left: 5px solid #2E86C1;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATA LOADING MODULE
# ==========================================
@st.cache_data
def load_database():
    """
    Loads the Customer.csv file to act as the Parcel Database.
    """
    try:
        df = pd.read_csv("Customer.csv")
        # Clean City names (remove trailing tabs/spaces found in your data)
        df['City'] = df['City'].str.strip()
        df['State'] = df['State'].str.strip()
        return df
    except FileNotFoundError:
        st.error("❌ 'Customer.csv' not found. Please upload the dataset.")
        return pd.DataFrame()

# ==========================================
# 2. GRAPH & SEARCH ALGORITHM MODULE
# ==========================================
def build_malaysia_logistics_graph():
    """
    Constructs a graph representing Malaysian Logistics Network.
    Nodes = Cities/States from your dataset.
    Edges = Simulated Roads/Flights with Cost (RM) and Time (Hrs).
    """
    G = nx.Graph()

    # Define major logistics hubs & connections (Simulated Data)
    # Format: (Node1, Node2, Cost_RM, Time_Hrs)
    
    # Central Region (Hub: Port Klang)
    routes = [
        ("Port Klang", "Shah Alam", 5, 0.5),
        ("Port Klang", "Kuala Lumpur", 10, 1.0),
        ("Port Klang", "Putrajaya", 15, 1.2),
        ("Shah Alam", "Petaling Jaya", 5, 0.4),
        ("Kuala Lumpur", "Petaling Jaya", 4, 0.3),
        ("Kuala Lumpur", "Ampang", 5, 0.5),
        
        # Northern Region
        ("Kuala Lumpur", "Ipoh", 40, 2.5),
        ("Ipoh", "Taiping", 20, 1.0),
        ("Ipoh", "Pulau Pinang", 35, 2.0),
        ("Pulau Pinang", "Alor Setar", 30, 1.5),
        ("Alor Setar", "Kangar", 15, 1.0),
        
        # Southern Region
        ("Putrajaya", "Seremban", 20, 1.0),
        ("Seremban", "Melaka", 30, 1.5),
        ("Melaka", "Muar", 25, 1.2),
        ("Muar", "Batu Pahat", 20, 1.0),
        ("Batu Pahat", "Johor Bahru", 35, 1.5),
        ("Johor Bahru", "Pasir Gudang", 10, 0.5),
        ("Johor Bahru", "Kota Tinggi", 15, 1.0),
        
        # East Coast
        ("Kuala Lumpur", "Kuantan", 60, 3.5),
        ("Kuantan", "Kuala Terengganu", 50, 2.5),
        ("Kuala Terengganu", "Kota Bharu", 45, 2.5),
        
        # East Malaysia (High Cost/Time due to flight/sea)
        ("Port Klang", "Kuching", 300, 24), # Ship/Flight
        ("Kuching", "Sibu", 50, 3.0),
        ("Sibu", "Bintulu", 60, 3.5),
        ("Bintulu", "Miri", 55, 3.0),
        ("Port Klang", "Kota Kinabalu", 350, 26),
        ("Kota Kinabalu", "Sandakan", 70, 5.0),
        ("Kota Kinabalu", "Tawau", 80, 6.0),
        ("Kota Kinabalu", "Keningau", 40, 2.5)
    ]

    for u, v, c, t in routes:
        G.add_edge(u, v, cost=c, time=t)

    return G

def find_optimal_route(G, start, end, mode):
    """
    Implements Dijkstra's Algorithm to find the shortest path.
    """
    weight_attr = 'cost' if mode == 'Lowest Cost (RM)' else 'time'
    
    try:
        path = nx.dijkstra_path(G, start, end, weight=weight_attr)
        cost = nx.dijkstra_path_length(G, start, end, weight=weight_attr)
        return path, cost
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None, None

# ==========================================
# 3. UI LAYOUT
# ==========================================
st.markdown('<p class="main-header">📦 Smart Parcel Routing System</p>', unsafe_allow_html=True)
st.write("### AI-Powered Logistics: Scan, Decode, and Optimize.")

# Sidebar Settings
st.sidebar.header("⚙️ Settings")
optimization_mode = st.sidebar.radio("Optimization Criteria:", ["Lowest Cost (RM)", "Fastest Time (Hours)"])
st.sidebar.info("This system uses **Computer Vision** to extract addresses from barcodes and **Dijkstra's Algorithm** to calculate optimal routes.")

# Create Tabs
tab1, tab2 = st.tabs(["📲 1. Scan Parcel", "🗺️ 2. Route Optimization"])

# --- TAB 1: SCANNING ---
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Barcode Image")
        uploaded_file = st.file_uploader("Upload a parcel image...", type=['png', 'jpg', 'jpeg'])
    
    scan_result = None
    
    if uploaded_file is not None:
        # 1. Process Image
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        
        with col1:
            st.image(image, caption="Uploaded Image", width=300)
        
        # 2. Decode Barcode
        barcodes = decode(img_array)
        
        if barcodes:
            scan_result = barcodes[0].data.decode("utf-8")
            st.session_state['scanned_id'] = scan_result  # Store in session
            
            with col2:
                st.success("✅ **Barcode Detected!**")
                st.markdown(f"<div class='metric-box'><h3>Order ID: {scan_result}</h3></div>", unsafe_allow_html=True)
                
                # 3. Lookup in Database
                df = load_database()
                customer_info = df[df['Order ID'] == scan_result]
                
                if not customer_info.empty:
                    row = customer_info.iloc[0]
                    st.write("---")
                    st.write(f"**👤 Customer:** {row['Customer Name']}")
                    st.write(f"**🏢 City:** {row['City']}")
                    st.write(f"**📍 State:** {row['State']}")
                    st.write(f"**📦 Product:** {row['Product Name']}")
                    
                    st.session_state['destination'] = row['City'] # Store destination
                else:
                    st.error("❌ Order ID not found in Customer Database.")
        else:
            st.error("⚠️ No barcode detected. Try a clearer image.")

# --- TAB 2: ROUTING ---
with tab2:
    st.subheader("🚀 Intelligent Route Planning")
    
    start_node = "Port Klang"
    end_node = st.session_state.get('destination', None)
    
    if end_node:
        G = build_malaysia_logistics_graph()
        
        # Check if destination exists in our graph
        if end_node not in G.nodes:
            # Fallback logic: try to route to the State capital if City is missing
            st.warning(f"⚠️ Direct route to '{end_node}' not mapped. Routing to nearest major hub.")
            # Simple heuristic mapping for demo purposes
            # (In a real app, you'd have a full coordinate mapping)
            end_node = "Kuala Lumpur" # Default fallback
        
        # Run Dijkstra
        path, value = find_optimal_route(G, start_node, end_node, optimization_mode)
        
        if path:
            c1, c2 = st.columns([3, 1])
            
            with c1:
                # Visualize Graph
                fig, ax = plt.subplots(figsize=(10, 6))
                pos = nx.kamada_kawai_layout(G)
                
                # Draw Base Graph
                nx.draw(G, pos, with_labels=True, node_color='lightgrey', node_size=500, font_size=8, edge_color='grey', alpha=0.5, ax=ax)
                
                # Highlight Path
                path_edges = list(zip(path, path[1:]))
                nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='#2E86C1', node_size=700, ax=ax)
                nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='#E74C3C', width=3, ax=ax)
                
                st.pyplot(fig)
            
            with c2:
                st.markdown("### 🏁 Route Details")
                st.write(f"**Start:** {start_node}")
                st.write(f"**End:** {end_node}")
                
                unit = "RM" if "Cost" in optimization_mode else "Hours"
                st.metric(label=f"Total {optimization_mode}", value=f"{value} {unit}")
                
                st.write("**Stops:**")
                for i, stop in enumerate(path):
                    st.code(f"{i+1}. {stop}")
        else:
            st.error(f"Could not find a path to {end_node}")
            
    else:
        st.info("👈 Please scan a parcel in Tab 1 first.")

# ==========================================
# ESG FOOTER
# ==========================================
st.write("---")
st.write("**🌱 ESG Impact:** Optimizing delivery routes reduces fuel consumption and carbon footprint (Environment) while ensuring timely essential deliveries (Social).")
