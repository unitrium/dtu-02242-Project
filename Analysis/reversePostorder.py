from typing import Dict, List, Set
from Parser import ProgramGraph, Node
from Parser.program_graph import Edge


def sort_rp(nodes: List[Node], rP: dict) -> List[Node]:
    return sorted(nodes, key=lambda node: rP[node.number])


def compute_reverse_post_order(prgmGraph: ProgramGraph):
    """Computes the reverse post order and returns the set of edges that constitute the spanning
    tree and the a dict indicating the reverse post order of each node.
    """
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
            dfs(node=edge.end, visited=visited, edges=edges, k=k, rP=rP, t=t)
            rP[node.number] = k
            k = k-1
