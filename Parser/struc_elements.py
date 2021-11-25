from typing import List, Union
VALID_A_OPERATORS = {"+", "-", "*", "/", "%"}
VALID_B_OPERATORS = {"&", "|", "not"}
VALID_R_OPERATORS = {">", "<", ">=", "<=", "=="}


class VariableAccess:
    """An object representing an access to a variable."""
    name: str
    child_accesses: "AExpr"
    variable_type: str
    rec_type: str

    def __init__(self, name: str, variable_type: str, rec_type: str = "", child_accesses: "AExpr" = None) -> None:
        self.name = name
        self.variable_type = variable_type
        if variable_type == "record":
            if not rec_type == "fst" and not rec_type == "snd":
                raise Exception(
                    "Record accessed without specifying .fst or .snd.")
            self.rec_type = rec_type
        elif variable_type == "array":
            if child_accesses is None:
                raise Exception("Array accessed without specifying the index")
            self.child_accesses = child_accesses

    def __str__(self) -> str:
        if self.variable_type == "variable":
            return self.name
        elif self.variable_type == "record":
            return f"{self.name}.{self.rec_type}"
        return f"{self.name}[{self.child_accesses}]"

    def copy(self) -> "VariableAccess":
        child_accesses = self.child_accesses.copy()
        return VariableAccess(self.name, self.variable_type, self.rec_type, child_accesses)


class Operation:
    """An object representing an operation between two variables."""
    right: Union["Operation", "AExpr"]
    left: Union["Operation", "AExpr"]
    operator: str

    def __init__(self, aexpr: "AExpr") -> None:
        if "*" in aexpr.expression:
            index = aexpr.expression.index("*")
            self.operator = "*"
        elif "/" in aexpr.expression:
            index = aexpr.expression.index("/")
            self.operator = "/"
        elif "%" in aexpr.expression:
            index = aexpr.expression.index("%")
            self.operator = "%"
        elif "+" in aexpr.expression:
            index = aexpr.expression.index("+")
            self.operator = "+"
        elif "-" in aexpr.expression:
            index = aexpr.expression.index("-")
            self.operator = "-"
        else:
            raise Exception("Not an operation.")
        left = AExpr(aexpr.expression[0:index])
        if len(left.expression) == 1:
            self.left = left
        else:
            self.left = Operation(left)
        right = AExpr(aexpr.expression[index+1:])
        if len(right.expression) == 1:
            self.right = right
        else:
            self.right = Operation(right)

    def __str__(self) -> str:
        return f"{self.left} {self.operator} {self.left}"


class AbstractExpr:
    """An abstract class representing an expression."""
    expression: List[Union[VariableAccess, str]]
    operation: Operation

    def __init__(self, expression: List[Union[VariableAccess, str]]) -> None:
        self.expression = []
        for expr in expression:
            self.expression.append(expr)
        try:
            self.operation = Operation(self)
        except Exception as err:
            pass

    def __str__(self) -> str:
        return " ".join([str(expr) for expr in self.expression])

    def copy(self) -> "AbstractExpr":
        """Deep copy of an expression."""
        new_expr = []
        for expr in self.expression:
            new = expr
            if isinstance(expr, VariableAccess):
                new = expr.copy()
            new_expr.append(new)
        return AbstractExpr(new_expr)

    def get_variables(self) -> List[VariableAccess]:
        """Returns a list of all the variables accessed in the expression."""
        variables = []
        for variable in self.expression:
            if isinstance(variable, VariableAccess):
                if variable.variable_type == "variable" or variable.variable_type == "record":
                    variables.append(variable)
                else:
                    for child in variable.child_accesses.get_variables():
                        variables.append(child)
        return variables


class AExpr(AbstractExpr):
    """An object representing an arithmetic expression."""

    def copy(self) -> "AExpr":
        """Deep copy of an expression."""
        new_expr = []
        for expr in self.expression:
            new = expr
            if isinstance(expr, VariableAccess):
                new = expr.copy()
            new_expr.append(new)
        return AExpr(new_expr)


class BExpr(AbstractExpr):
    """An object representing an arithmetic expression."""

    def copy(self) -> "BExpr":
        """Deep copy of an expression."""
        new_expr = []
        for expr in self.expression:
            new = expr
            if isinstance(expr, VariableAccess):
                new = expr.copy()
            new_expr.append(new)
        return BExpr(new_expr)
