#!/usr/bin/env python3
from collections import deque, defaultdict
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
    for node in list(g.keys()):
        g[node] = sorted(g[node])
    return g

def full_bfs(graph: Dict[str, List[str]], start: str = 'A') -> Tuple[List[str], Dict[str, int]]:
    visited: Set[str] = set()
    order: List[str] = []
    levels: Dict[str, int] = {}
    all_nodes = sorted(graph.keys())

    def bfs_from_root(root: str):
        q = deque()
        q.append((root, 0))
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
        if start not in visited:
            dfs(start)
    for node in all_nodes:
        if node not in visited:
            dfs(node)
    return order

def print_bfs_result(order: List[str], levels: Dict[str, int]):
    print("BFS visitation order:", ", ".join(order))
    level_groups = defaultdict(list)
    for node, lvl in levels.items():
        level_groups[lvl].append(node)
    print("BFS levels (per component root):")
    for lvl in sorted(level_groups.keys()):
        nodes = sorted(level_groups[lvl])
        print(f"  Level {lvl}: {{ {', '.join(nodes)} }}")

def print_dfs_result(order: List[str]):
    print("DFS visitation order:", ", ".join(order))

def main():
    graph = build_graph()
    for n in sorted(graph.keys()):
        print(f"{n} -> {graph[n]}")
    bfs_order, bfs_levels = full_bfs(graph, start='A')
    print_bfs_result(bfs_order, bfs_levels)
    dfs_order = full_dfs(graph, start='A')
    print_dfs_result(dfs_order)

if __name__ == "__main__":
    main()
