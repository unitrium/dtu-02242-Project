"""Converts AST to program graph."""
"""Program graph structure is a dict whose keys are the index of the nodes. Under each item is a dict with nodes reachable from this node and action."""


from typing import Dict, List, Set, Tuple
from .parser import grammar
from lark import Tree, Token
POSSIBLE_ACTIONS = ["assign_var", "assign_arr",
                    "assign_rec", "read", "write", "boolean"]


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
        self.outgoing_edges = []


class Action:
    action_type: str
    variables: List[str]
    label: str

    def __init__(self, action_type: str, variables: List[str], label: str) -> None:
        if action_type not in POSSIBLE_ACTIONS:
            raise Exception(f"Unknown action: {action_type}")
        self.action_type = action_type
        self.variables = variables
        self.label = label

    def __str__(self) -> str:
        return self.label


class Edge:
    start: Node
    end: Node
    action: str

    def __init__(self, start: Node, end: Node, action: Action) -> None:
        self.start = start
        self.end = end
        self.action = action

    def __str__(self) -> str:
        end = 'End node' if self.end.last else ''
        return f"Node {self.start.number} ({id(self.start)}) to node \
         {self.end.number} ({id(self.end)}) with action {self.action} {end}"


class ProgramGraph:
    nodes: Dict[int, Node]
    edges: List[Edge]
    variables: Dict[str, Set]

    def __init__(self, program: str) -> None:
        tree = grammar.parse(program)
        self.edges, init_node = high_level_edges(tree)
        check_edges(self.edges)
        self.nodes = {
            0: init_node
        }
        self.__explore_nodes()
        self.variables = {
            "variable": set(),
            "array": set(),
            "record": set()
        }
        get_all_variables(tree, self.variables)

    def get_edges(self) -> List[Edge]:
        """Returns a deep copy of the edges."""
        return [edge for edge in self.edges]

    def get_nodes(self) -> List[Node]:
        """Returns a deep copy of the nodes as a list."""
        return [node for node in self.nodes.values()]

    def __explore_nodes(self):
        """Parses the edges to find all nodes."""
        edges_to_explore = self.get_edges()
        while len(edges_to_explore) > 0:
            edge = edges_to_explore.pop()
            self.nodes[edge.end.number] = edge.end


def compute_edges(start: Node, end: Node, tree: Tree) -> Set[Edge]:
    if tree.data == "assignment" or tree.data == "read" or tree.data == "write":
        action: Action = None
        # Parsing the Tree to get the variable that is being accessed.
        variable, variable_type = expand_access(tree.children[0])
        if tree.data == "assignment":
            # Parsing the Tree to get the value the variable is being assigned to.
            value = beautiful_expr(expand_a_expr(tree.children[1]))

            action = Action(f"assign_{variable_type}", [
                            variable], f"{variable} := {value}")
        elif tree.data == "read":
            action = Action("read", [variable], f"read {variable}")
        else:
            action = Action("write", [variable], f"write {variable}")
        edge = Edge(start, end, action)
        start.outgoing_edges.append(edge)
        return [edge]
    elif tree.data == "if" or tree.data == "else" or tree.data == "while":
        b_expr = expand_b_expr(tree.children[0])
        not_b_expr = ["not"] + b_expr
        if_branch_node = Node(start.number+1)
        end.number = if_branch_node.number+1
        if_action = Action("boolean", [], label=beautiful_expr(b_expr))
        if_edge = Edge(start, if_branch_node, if_action)
        else_edge: Edge = None
        else_action = Action(
            "boolean", [], label=beautiful_expr(not_b_expr))
        if tree.data == "else":
            else_branch_node = Node(if_branch_node.number+1)
            end.number = else_branch_node.number+1
            else_edge = Edge(start, else_branch_node,
                             else_action)
            additional_edges = compute_edges(
                if_branch_node, end, tree.children[1]) + compute_edges(else_branch_node, end, tree.children[2])
        else:  # if and while
            else_edge = Edge(start, end, else_action)
            if tree.data == "if":
                additional_edges = compute_edges(
                    if_branch_node, end, tree.children[1])
            else:  # while branching
                end.number += 1
                additional_edges = compute_edges(
                    if_branch_node, start, tree.children[1])
        start.outgoing_edges.append(if_edge)
        start.outgoing_edges.append(else_edge)
        return [if_edge, else_edge] + additional_edges
    elif tree.data == "statement":
        end.number = start.number + 1
        return compute_edges(start, end, tree.children[0])


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
            var, _ = expand_access(child)
            expr.append(var)
        elif child.data == "opa":
            var, _ = expand_opa(child)
            expr.append(var)
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


def expand_access(tree: Tree) -> Tuple[str, str]:
    """Given an access tree returns the variable access and the type of access.
    var: variable access, arr: array access, rec: record access.
    """
    tree = tree.children[0]
    if tree.data == 'variable':
        return tree.children[0].value, "var"
    elif tree.data == "record_access":
        variable_name = tree.children[0].children[0].children[0].value
        if tree.children[0].data == "record_fst_access":
            return f"{variable_name}.fst", "rec"
        else:
            return f"{variable_name}.snd", "rec"
    else:  # Array access
        variable_name = tree.children[0].children[0].value
        if isinstance(tree.children[1], Token):  # Case direct number
            return f"{variable_name}[{tree.children[1].value}]", "arr"
        else:  # Another access to dig in
            expr, _ = expand_access(tree.children[1])
            return f"{variable_name}[{expr}]", "arr"


def get_all_variables(tree: Tree, variables: Dict):
    """Returns all variables that will be encountered"""
    if tree.data == "variable":
        variables["variable"].add(tree.children[0].value)
    elif tree.data == "record_access":
        variables["record"].add(tree.children[0].children[0].children[0].value)
    elif tree.data == "array_access":
        variables["array"].add(tree.children[0].children[0].value)
        if isinstance(tree.children[1], Tree):
            get_all_variables(tree.children[1], variables)
    else:
        for child in tree.children:
            if isinstance(child, Tree):
                get_all_variables(child, variables)
