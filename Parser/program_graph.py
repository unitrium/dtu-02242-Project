"""Converts AST to program graph."""
"""Program graph structure is a dict whose keys are the index of the nodes. Under each item is a dict with nodes reachable from this node and action."""




from typing import List, Set, Tuple
from lark import Tree, Token
class Node:
    """
    A class representing a node in a program graph.
    The initial node has number 0.
    The final node has the boolean set to true.
    """
    number: int
    last: bool
    outgoing_edges: List["Edge"]

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
        end = 'End node' if self.end.last else ''
        return f"Node {self.start.number} ({id(self.start)}) to node \
         {self.end.number} ({id(self.end)}) with action {self.label} {end}"


def compute_edges(start: Node, end: Node, action: Tree) -> Set[Edge]:
    if action.data == "assignment" or action.data == "read" or action.data == "write":
        edge = None
        if action.data == "assignment":
            # Parsing the Tree to get the variable that is being assigned.
            variable = expand_access(action.children[0])
            # Parsing the Tree to get the value the variable is being assigned to.
            value = beautiful_expr(expand_a_expr(action.children[1]))
            edge = Edge(start, end, f"{variable} := {value}")
        elif action.data == "read":
            edge = Edge(
                start, end, f"read {expand_access(action.children[0])}")
        else:
            edge = Edge(
                start, end, f"write {expand_access(action.children[0])}")
        start.outgoing_edges.append(edge)
        return [edge]
    elif action.data == "if" or action.data == "else" or action.data == "while":
        b_expr = expand_b_expr(action.children[0])
        not_b_expr = ["not"] + b_expr
        if_branch_node = Node(start.number+1)
        end.number = if_branch_node.number+1
        if_edge = Edge(start, if_branch_node, beautiful_expr(b_expr))
        else_edge = None
        if action.data == "else":
            else_branch_node = Node(if_branch_node.number+1)
            end.number = else_branch_node.number+1
            else_edge = Edge(start, else_branch_node,
                             beautiful_expr(not_b_expr))
            additional_edges = compute_edges(
                if_branch_node, end, action.children[1]) + compute_edges(else_branch_node, end, action.children[2])
        else:  # if and while
            else_edge = Edge(start, end, beautiful_expr(not_b_expr))
            if action.data == "if":
                additional_edges = compute_edges(
                    if_branch_node, end, action.children[1])
            else:  # while branching
                end.number += 1
                additional_edges = compute_edges(
                    if_branch_node, start, action.children[1])
        start.outgoing_edges.append(if_edge)
        start.outgoing_edges.append(else_edge)
        return [if_edge, else_edge] + additional_edges
    elif action.data == "statement":
        end.number = start.number + 1
        return compute_edges(start, end, action.children[0])


def high_level_edges(tree: Tree) -> Tuple[List[Edge], Node]:
    """High level function to create a program grah, returns a set of edges and the initial node."""
    if tree.data == "program":
        start_node = Node(0)
        init_node = start_node
        end_node = Node(-1)
        edges: List[Edge] = []
        for child in tree.children:
            edges += compute_edges(start_node, end_node, child)
            start_node = end_node
            end_node = Node(end_node.number)
        start_node.last = True
        return edges, init_node
    else:
        raise Exception("Supplied tree does not start with program.")


def check_edges(edges: List[Edge]):
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


def expand_a_expr(tree: Tree) -> List[str]:
    """Given an a_expr tree unfolds the a_expr"""
    expr = []
    for child in tree.children:
        if isinstance(child, Token):
            expr.append(child.value)
        elif child.data == "access":
            expr.append(expand_access(child))
        elif child.data == "opa":
            expr.append(expand_opa(child))
        else:  # Case nested in another opa
            for expr_a in expand_a_expr(child):
                expr.append(expr_a)
    return expr


def expand_b_expr(tree: Tree) -> List[str]:
    expr = []
    for child in tree.children:
        if isinstance(child, Token):
            expr.append(child.value)
        elif child.data == "a_expr":
            for expr_a in expand_a_expr(child):
                expr.append(expr_a)
        elif child.data == "opr":
            expr.append(expand_opr(child))
        elif child.data == "opb":
            expr.append(expand_opb(child))
        else:  # Case nested in another opa
            if child.data == "not":
                expr.append("not")
            for expr_b in expand_b_expr(child):
                expr.append(expr_b)
    return expr


def beautiful_expr(unfold_expr: List[str]) -> str:
    return " ".join(unfold_expr)


def expand_opa(tree: Tree) -> str:
    child = tree.children[0]
    if child.data == "add":
        return "+"
    elif child.data == "sub":
        return "-"
    elif child.data == "mul":
        return "*"
    elif child.data == "div":
        return "/"
    elif child.data == "mod":
        return "%"


def expand_opr(tree: Tree) -> str:
    child = tree.children[0]
    if child.data == "inf":
        return "<"
    elif child.data == "infe":
        return "<="
    elif child.data == "sup":
        return ">"
    elif child.data == "supe":
        return ">="
    elif child.data == "eq":
        return "=="
    else:
        return "!="


def expand_opb(tree: Tree) -> str:
    child = tree.children[0]
    if child.data == "and":
        return "&"
    elif child.data == "or":
        return "|"


def expand_access(tree: Tree) -> str:
    """Given an access tree returns the variable access."""
    tree = tree.children[0]
    if tree.data == 'variable':
        return tree.children[0].value
    elif tree.data == "record_access":
        variable_name = tree.children[0].children[0].children[0].value
        if tree.children[0].data == "record_fst_access":
            return f"{variable_name}.fst"
        else:
            return f"{variable_name}.snd"
    else:  # Array access
        variable_name = tree.children[0].children[0].value
        if isinstance(tree.children[1], Token):  # Case direct number
            return f"{variable_name}[{tree.children[1].value}]"
        else:  # Another access to dig in
            return f"{variable_name}[{expand_access(tree.children[1].children[0])}]"


program_graph = {

}
