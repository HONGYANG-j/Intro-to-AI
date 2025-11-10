import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, deque
from typing import Dict, List, Tuple
from PIL import Image

# --- Graph Utility Functions ---

def build_graph() -> Dict[str, List[str]]:
    g = {
        'A': ['B', 'D'],
        'B': ['C', 'E', 'G'],
        'C': ['A'],
        'D': ['C'],
        'E': ['H'],
        'F': [],
        'G': ['F'],
        'H': ['F', 'G'],
    }
    for node in g:
        g[node] = sorted(g[node])
    return g


def full_bfs(graph: Dict[str, List[str]], start: str = 'A') -> Tuple[List[str], Dict[str, int]]:
    visited, order, levels = set(), [], {}
    all_nodes = sorted(graph.keys())

    def bfs_from_root(root):
        q = deque([(root, 0)])
        visited.add(root)
        levels[root] = 0
        while q:
            node, lvl = q.popleft()
            order.append(node)
            for nb in graph.get(node, []):
                if nb not in visited:
                    visited.add(nb)
                    levels[nb] = lvl + 1
                    q.append((nb, lvl + 1))

    if start in all_nodes:
        bfs_from_root(start)
    for node in all_nodes:
        if node not in visited:
            bfs_from_root(node)
    return order, levels


def full_dfs(graph: Dict[str, List[str]], start: str = 'A') -> List[str]:
    visited, order = set(), []
    all_nodes = sorted(graph.keys())

    def dfs(node):
        visited.add(node)
        order.append(node)
        for nb in graph.get(node, []):
            if nb not in visited:
                dfs(nb)

    if start in all_nodes:
        dfs(start)
    for node in all_nodes:
        if node not in visited:
            dfs(node)
    return order


# --- Streamlit App ---

st.set_page_config(page_title="Graph Traversal Visualizer", page_icon="🌐")

# Section 1: Graph Image
st.title("Graph Representation")

try:
    image = Image.open("Lab-Report/Lab-Report-1/LabReport_BSD2513_#1.jpg")
    st.image(image, caption="Directed Graph Example", use_container_width=True)
except FileNotFoundError:
    st.warning("⚠️ Graph image not found. Please check the file name or path.")

st.markdown("---")

# Section 2: Graph Traversal Visualizer
st.title("🌐 Graph Traversal Visualizer")
st.markdown("Visualize **Breadth-First Search (BFS)** and **Depth-First Search (DFS)** on a directed graph.")

graph = build_graph()

st.subheader("Graph Adjacency List")
for node in sorted(graph.keys()):
    st.write(f"**{node} →** {graph[node]}")

start_node = st.selectbox("Choose a start node:", sorted(graph.keys()))
method = st.radio("Choose traversal method:", ["BFS", "DFS"])

# Section 3: Run Traversal
if st.button("Run Traversal"):
    if method == "BFS":
        order, levels = full_bfs(graph, start=start_node)
        st.success(f"**BFS Order:** {', '.join(order)}")

        st.subheader("Node Levels")
        groups = defaultdict(list)
        for n, l in levels.items():
            groups[l].append(n)
        for lvl in sorted(groups):
            st.write(f"**Level {lvl}:** {', '.join(sorted(groups[lvl]))}")
    else:
        order = full_dfs(graph, start=start_node)
        st.success(f"**DFS Order:** {', '.join(order)}")

    # Draw the Graph
    G = nx.DiGraph()
    for n, nbrs in graph.items():
        for nb in nbrs:
            G.add_edge(n, nb)

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(6, 4))
    nx.draw(G, pos, with_labels=True, node_size=900, node_color="#a2d2ff", arrowsize=18)
    st.pyplot(plt.gcf())
    plt.clf()

