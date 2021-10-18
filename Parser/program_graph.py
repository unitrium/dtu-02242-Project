"""Converts AST to program graph."""
"""Program graph structure is a dict whose keys are the index of the nodes. Under each item is a dict with nodes reachable from this node and action."""




from typing import Set
from lark import Tree, Token
class Node:
    """A class representing a node in a program graph. The initial node has number 0. The final node has the boolean set to true."""
    number: int
    last: bool

    def __init__(self, number: int, last: bool = False) -> None:
        self.number = number
        self.last = last


class Edge:
    start: Node
    end: Node
    label: str

    def __init__(self, start: Node, end: Node, label: str) -> None:
        self.start = start
        self.end = end
        self.label = label

    def __str__(self) -> str:
        return f"Node {self.start.number} to node {self.end.number} with action {self.label}"


def edges(start: Node, end: Node, action: Tree) -> Set[Edge]:
    if action.data == "assignment":
        # Parsing the Tree to get the variable that is being assigned.
        variable = None
        access = action.children[0].children[0]
        if access.data == "record_access":
            variable_name = access.children[0].children[0].children[0].value
            if access.children[0].data == "record_fst_access":
                variable = f"{variable_name}.fst"
            else:
                variable = f"{variable_name}.snd"
        # Parsing the Tree to get the value the variable is being assigned to.
        value = None
        a_expr = action.children[1]
        if isinstance(a_expr.children[0], Token):
            value = a_expr.children[0].value
        return Edge(start, end, f"{variable} := {value}")


program_graph = {

}
