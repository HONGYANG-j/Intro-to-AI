#!/usr/bin/env python3
import streamlit as st
from collections import deque, defaultdict
from typing import Dict, List, Tuple, Set

# ---------- GRAPH SETUP ----------
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
    for node in list(g.keys()):
        g[node] = sorted(g[node])
    return g

# ---------- BFS ----------
def full_bfs(graph: Dict[str, List[str]], start: str = 'A') -> Tuple[List[str], Dict[str, int]]:
    visited: Set[str] = set()
    order: List[str] = []
    levels: Dict[str, int] = {}
    all_nodes = sorted(graph.keys())

    def bfs_from_root(root: str):
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

# ---------- DFS ----------
def full_dfs(graph: Dict[str, List[str]], start: str = 'A') -> List[str]:
    visited: Set[str] = set()
    order: List[str] = []
    all_nodes = sorted(graph.keys())

    def dfs(node: str):
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

# ---------- STREAMLIT APP ----------
st.set_page_config(page_title="Graph Traversal Visualizer", page_icon="🌐")

st.title("🌐 Graph Traversal Visualizer")
st.markdown("""
Visualize **Breadth-First Search (BFS)** and **Depth-First Search (DFS)**  
on a simple directed graph.
""")

# Build and show the graph
graph = build_graph()

st.subheader("Graph Adjacency List")
for node in sorted(graph.keys()):
    st.write(f"**{node} →** {graph[node]}")

# Controls
start_node = st.selectbox("Choose a start node:", sorted(graph.keys()), index=0)
traversal = st.radio("Choose traversal type:", ["BFS", "DFS"])

# Run traversal
if st.button("Run Traversal"):
    if traversal == "BFS":
        order, levels = full_bfs(graph, start=start_node)
        st.success(f"BFS Visitation Order: {', '.join(order)}")

        st.subheader("BFS Levels")
        level_groups = defaultdict(list)
        for node, lvl in levels.items():
            level_groups[lvl].append(node)
        for lvl in sorted(level_groups.keys()):
            st.write(f"**Level {lvl}:** {', '.join(sorted(level_groups[lvl]))}")

    else:
        order = full_dfs(graph, start=start_node)
        st.success(f"DFS Visitation Order: {', '.join(order)}")
