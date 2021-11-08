from typing import Dict, List, Set
from Parser import ProgramGraph, Node
from Parser.program_graph import Edge


def compute_reverse_post_order(prgmGraph: ProgramGraph):
    nodes = prgmGraph.get_nodes()
    edges = prgmGraph.get_edges()
    rP = {}
    t = set()
    visited = set()
    k = len(nodes)
    dfs(nodes[0], visited, edges, k, rP, t)
    return t, rP


def dfs(node: Node, visited: Set[Node], edges: List[Edge], k: int, rP: Dict, t: set):
    visited.add(node.number)
    for edge in node.outgoing_edges:
        if edge.end.number not in visited:
            t.add(f"{edge.start.number}, {edge.end.number}")
            rP[edge.start.number] = k
            k = k-1
            dfs(node=edge.end, visited=visited, edges=edges, k=k, rP=rP, t=t)
