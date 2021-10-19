"""Converts AST to program graph."""
"""Program graph structure is a dict whose keys are the index of the nodes. Under each item is a dict with nodes reachable from this node and action."""




from typing import List, Set
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
        variable = expand_access(action.children[0])

        # Parsing the Tree to get the value the variable is being assigned to.
        value = beautiful_expr(expand_a_expr(action.children[1]))
        return Edge(start, end, f"{variable} := {value}")
    elif action.data == "if" or action.data == "else" or action.data == "while":
        b_expr = expand_b_expr(action.children[0])
        not_b_expr = ["not"] + b_expr
        return Edge(start, end, f"{beautiful_expr(b_expr)}")
    elif action.data == "read":
        return Edge(start, end, f"read {expand_access(action.children[0])}")
    elif action.data == "write":
        return Edge(start, end, f"write {expand_access(action.children[0])}")


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


def beautiful_expr(unfold_expr: List[str]):
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
