import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from graph_utils import build_graph, full_bfs, full_dfs

st.set_page_config(page_title="Graph Traversal Visualizer", page_icon="🌐")

st.title("🌐 Graph Traversal Visualizer")
st.markdown("Visualize **Breadth-First Search (BFS)** and **Depth-First Search (DFS)** on a directed graph.")

graph = build_graph()

st.subheader("Graph Adjacency List")
for node in sorted(graph.keys()):
    st.write(f"**{node} →** {graph[node]}")

start_node = st.selectbox("Choose a start node:", sorted(graph.keys()))
method = st.radio("Choose traversal method:", ["BFS", "DFS"])

if st.button("Run Traversal"):
    if method == "BFS":
        order, levels = full_bfs(graph, start=start_node)
        st.success(f"BFS Order: {', '.join(order)}")
        st.subheader("Levels")
        groups = defaultdict(list)
        for n, l in levels.items():
            groups[l].append(n)
        for lvl in sorted(groups):
            st.write(f"**Level {lvl}:** {', '.join(sorted(groups[lvl]))}")
    else:
        order = full_dfs(graph, start=start_node)
        st.success(f"DFS Order: {', '.join(order)}")

    G = nx.DiGraph()
    for n, nbrs in graph.items():
        for nb in nbrs:
            G.add_edge(n, nb)
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(6, 4))
    nx.draw(G, pos, with_labels=True, node_size=900, node_color="#a2d2ff", arrowsize=18)
    st.pyplot(plt.gcf())
    plt.clf()
