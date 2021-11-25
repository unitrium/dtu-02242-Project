"""Converts AST to program graph."""


from typing import Dict, List, Set, Tuple, Union
from .parser import grammar
from .struc_elements import AExpr, BExpr, VariableAccess, VariableDeclaration
from lark import Tree, Token
from .utils import check_edges
POSSIBLE_ACTIONS = ["assign", "read", "write", "boolean", "declare"]


class Node:
    """
    A class representing a node in a program graph.
    The initial node has number 0.
    The final node has the boolean set to true.
    """
    number: int
    last: bool
    outgoing_edges: List["Edge"]
    incoming_edges: List["Edge"]

    def __init__(self, number: int, last: bool = False) -> None:
        self.number = number
        self.last = last
        self.outgoing_edges = []
        self.incoming_edges = []


class Action:
    """
    A class representing an action.
    action_type: str the type of the action can be assign, read, write, declare, boolean
    variable: VariableAccess the variable that is being set.
    right_expression: Union[AExpr, BExpr] the expression that is on the right of an assignment.
    Fx: A[b+1] = a+c that would be a+c.
    For a boolean expression the right expression is the boolean expression itself.
    """
    action_type: str
    variable: Union[VariableAccess, VariableDeclaration]
    right_expression: Union[AExpr, BExpr]

    def __init__(self, action_type: str, variable: Union[VariableAccess, VariableDeclaration] = None, right_expression: Union[AExpr, BExpr] = None) -> None:
        if action_type not in POSSIBLE_ACTIONS:
            raise Exception(f"Unknown action: {action_type}")
        elif action_type == "assign":
            if not variable:
                raise Exception(
                    "Creating assign action without specifying the left variable.")
            elif not right_expression:
                raise Exception(
                    "Creating action without specifying the right expression.")
        self.action_type = action_type
        self.variable = variable
        self.right_expression = right_expression

    def __str__(self) -> str:
        if self.action_type == "assign":
            return f"{self.variable} := {self.right_expression}"
        elif self.action_type == "read" or self.action_type == "write":
            return f"{self.action_type} {self.variable}"
        elif self.action_type == "boolean":
            return str(self.right_expression)


class Edge:
    start: Node
    end: Node
    action: Action

    def __init__(self, start: Node, end: Node, action: Action) -> None:
        self.start = start
        self.end = end
        self.action = action
        self.start.outgoing_edges.append(self)
        self.end.incoming_edges.append(self)

    def __str__(self) -> str:
        end = 'End node' if self.end.last else ''
        return f"Node {self.start.number} ({id(self.start)}) to node \
         {self.end.number} ({id(self.end)}) with action {self.action} {end}"


class ProgramGraph:
    nodes: Dict[int, Node]
    edges: List[Edge]
    variables: Dict[str, Dict[str, VariableDeclaration]]

    def __init__(self, program: str) -> None:
        tree = grammar.parse(program)
        self.edges, init_node = high_level_edges(tree)
        check_edges(self.edges)
        self.nodes = {
            0: init_node
        }
        self.__explore_nodes()
        variables = {
            "variable": set(),
            "array": set(),
            "record": set()
        }
        get_all_variables(tree, variables)
        self.variables = get_all_declared_variables(variables, self.edges)

    def get_edges(self) -> List[Edge]:
        """Returns a deep copy of the edges."""
        return [edge for edge in self.edges]

    def get_nodes(self) -> List[Node]:
        """Returns a deep copy of the nodes as a list."""
        return [node for node in self.nodes.values()]

    def get_last_node(self) -> Node:
        """Returns the last node of the program graph."""
        return self.nodes[len(self.nodes)-1]

    def __explore_nodes(self):
        """Parses the edges to find all nodes."""
        edges_to_explore = self.get_edges()
        while len(edges_to_explore) > 0:
            edge = edges_to_explore.pop()
            self.nodes[edge.end.number] = edge.end


def compute_edges(start: Node, end: Node, tree: Tree) -> List[Edge]:
    if tree.data == "assignment" or tree.data == "read" or tree.data == "write":
        action: Action = None
        # Parsing the Tree to get the variable that is being accessed.
        variable = expand_access(tree.children[0])
        if tree.data == "assignment":
            # Parsing the Tree to get the value the variable is being assigned to.
            value = expand_a_expr(tree.children[1])

            action = Action("assign", variable, value)
        elif tree.data == "read":
            action = Action("read", variable)
        else:
            action = Action("write", variable)
        edge = Edge(start, end, action)
        return [edge]
    elif tree.data == "if" or tree.data == "else" or tree.data == "while":
        b_expr = expand_b_expr(tree.children[0])
        not_b_expr = BExpr(["not"] + b_expr.copy().expression)
        if_branch_node = Node(start.number+1)
        end.number = if_branch_node.number+1
        if_action = Action("boolean", right_expression=b_expr)
        if_edge = Edge(start, if_branch_node, if_action)
        else_edge: Edge = None
        else_action = Action(
            "boolean", right_expression=not_b_expr)
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
        return [if_edge, else_edge] + additional_edges
    elif tree.data == "statement":
        end.number = start.number + 1
        return compute_edges(start, end, tree.children[0])
    elif tree.data == "declaration":
        end.number = start.number + 1
        variable = None
        if tree.children[0].data == "var_declare":
            variable = VariableDeclaration(
                name=tree.children[0].children[0].children[0].value,
                variable_type="variable"
            )
        elif tree.children[0].data == "arr_declare":
            variable = VariableDeclaration(
                name=tree.children[0].children[1].children[0].value,
                variable_type="array",
                array_len=tree.children[0].children[0].value
            )
        else:
            variable = VariableDeclaration(
                name=tree.children[0].children[0].children[0].value,
                variable_type="record"
            )
        return [Edge(start, end, Action("declare", variable))]


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


def expand_a_expr(tree: Tree) -> AExpr:
    """Given an a_expr tree unfolds the a_expr"""
    expr = []
    for child in tree.children:
        if isinstance(child, Token):
            expr.append(child.value)
        elif child.data == "access":
            var = expand_access(child)
            expr.append(var)
        elif child.data == "opa":
            var = expand_opa(child)
            expr.append(var)
        else:  # Case nested in another opa
            for expr_a in expand_a_expr(child).expression:
                expr.append(expr_a)
    return AExpr(expr)


def expand_b_expr(tree: Tree) -> BExpr:
    expr = BExpr([])
    for child in tree.children:
        if isinstance(child, Token):
            expr.expression.append(child.value)
        elif child.data == "a_expr":
            expr.expression.append(expand_a_expr(child))
        elif child.data == "opr":
            expr.expression.append(expand_opr(child))
        elif child.data == "opb":
            expr.expression.append(expand_opb(child))
        else:  # Case nested in another opa
            if child.data == "not":
                expr.expression.append("not")
            expr.expression.append(expand_b_expr(child))
    return expr


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


def expand_access(tree: Tree) -> VariableAccess:
    """Given an access tree returns the variable access and the type of access.
    var: variable access, arr: array access, rec: record access.
    """
    tree = tree.children[0]
    if tree.data == 'variable':
        return VariableAccess(tree.children[0].value, "variable")
    elif tree.data == "record_access":
        variable_name = tree.children[0].children[0].children[0].value
        if tree.children[0].data == "record_fst_access":
            return VariableAccess(variable_name, "record", "fst")
        else:
            return VariableAccess(variable_name, "record", "snd")
    else:  # Array access
        variable_name = tree.children[0].children[0].value
        if isinstance(tree.children[1], Token):  # Case direct number
            return VariableAccess(variable_name, "array", child_accesses=AExpr([tree.children[1].value]))
        else:  # Another access to dig in
            a_expr = expand_a_expr(tree.children[1])
            return VariableAccess(variable_name, "array", child_accesses=a_expr)


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
    elif tree.data == "declaration":
        pass
    else:
        for child in tree.children:
            if isinstance(child, Tree):
                get_all_variables(child, variables)


def get_all_declared_variables(variables: Dict, edges: List[Edge]) -> Dict:
    """Gets all declared variables and returns an error if a variable as not been declared."""
    declarations = {
        "variable": dict(),
        "array": dict(),
        "record": dict()
    }
    for edge in filter(lambda x: isinstance(x.action.variable, VariableDeclaration), edges):
        declarations[edge.action.variable.variable_type][edge.action.variable.name] = edge.action.variable
    for variable_type, var in variables.items():
        for var_name in var:
            if var_name not in declarations[variable_type]:
                raise Exception(f"Variable {var_name} not declared.")
    return declarations
