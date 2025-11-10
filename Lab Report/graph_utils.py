# graph_utils.py
from collections import deque
from typing import Dict, List, Tuple, Set

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
