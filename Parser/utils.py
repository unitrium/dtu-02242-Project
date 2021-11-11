from typing import List


def check_edges(edges: List["Edge"]):
    """Check the coherence of a graph."""
    flat = {}
    for edge in edges:
        if edge.start.number not in flat:
            flat[edge.start.number] = id(edge.start)
        elif flat[edge.start.number] != id(edge.start):
            raise Exception(
                f"Incoherent graph. Node {edge.start.number} is present twice but with different objects.")
        if edge.end.number not in flat:
            flat[edge.end.number] = id(edge.end)
        elif flat[edge.end.number] != id(edge.end):
            raise Exception(
                f"Incoherent graph. Node {edge.end.number} is present twice but with different objects.")
