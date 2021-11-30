from typing import List, Union
VALID_A_OPERATORS = {"+", "-", "*", "/", "%"}
VALID_B_OPERATORS = {"&", "|", "not"}
VALID_R_OPERATORS = {">", "<", ">=", "<=", "=="}


class VariableDeclaration:
    """
    An object representing a variable declaration. Fx: int[3] A;
    Used to store informations about a variable.
    name: str Name of the variable
    variable_type: str can be variable, array or record.
    array_len: int in the case of an array the length of the array.
    """
    name: str
    variable_type: str
    array_len: int

    def __init__(self, name: str, variable_type: str, array_len: int = None) -> None:
        self.name = name
        if variable_type not in ["variable", "array", "record"]:
            raise Exception(f"Invalid variable type: {variable_type}")
        self.variable_type = variable_type
        if variable_type == "array" and array_len is None:
            raise Exception(f"Array length needs to be specified.")
        self.array_len = array_len

    def __str__(self) -> str:
        if self.variable_type == "variable":
            return f"int {self.name}"
        elif self.variable_type == "record":
            return "{int fst; int snd} " + self.name
        return f"int[{self.array_len}] {self.name}"


class VariableAccess:
    """
    An object representing an access to a variable. Fx: a command accessing the variable a, or A[1] or R.fst.
    name: str Name of the variable
    child_accesses: AExpr in the case of an array the arithemetic expression computing the index.
    variable_type: str can be variable, array or record.
    rec_type: str in the case of a record specify wether it's fst or snd.
    """
    name: str
    child_accesses: "AExpr"
    variable_type: str
    rec_type: str

    def __init__(self, name: str, variable_type: str, rec_type: str = "", child_accesses: "AExpr" = None) -> None:
        self.name = name
        if variable_type not in ["variable", "array", "record"]:
            raise Exception(f"Invalid variable type: {variable_type}")
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


class BooleanOperation:
    """An object representing a boolean operation."""
    right: Union["BooleanOperation", "AbstractExpr"]
    left: Union["BooleanOperation", "AbstractExpr"]
    operator: str

    def __init__(self, bexpr: "BExpr") -> None:
        if "&" in bexpr.expression:
            index = bexpr.expression.index("&")
            self.operator = "&"
        elif "|" in bexpr.expression:
            index = bexpr.expression.index("|")
            self.operator = "|"
        elif "not" in bexpr.expression:
            index = bexpr.expression.index("not")
            self.operator = "not"
        # No more boolean operators this is now a relational operation.
        else:
            self.__relative_init(bexpr)
            return
        left = BExpr(bexpr.expression[0: index])
        if not self.operator == "not":
            self.left = BooleanOperation(left)
        # not operator will have the left empty.
        else:
            self.left = None
        right = BExpr(bexpr.expression[index+1:])
        self.right = BooleanOperation(right)

    def is_relational(self) -> bool:
        """Indicates whether the operation is a relational boolean operaton."""
        return self.operator in VALID_R_OPERATORS

    def __str__(self) -> str:
        return f"{'' if self.left is None else self.left} {self.operator} {self.right}"

    def __relative_init(self, bexpr: "BExpr") -> None:
        """To call to initialize the operation as a relative operation."""
        nb_relative_operations = 0
        for r_operator in VALID_R_OPERATORS:
            if r_operator in bexpr.expression:
                nb_relative_operations += 1
                index = bexpr.expression.index(r_operator)
                self.operator = r_operator
        if nb_relative_operations != 1:
            print(bexpr)
            raise Exception(
                f"Error a relative operation was supplied with 0 or multiple relational operators. {bexpr}")
        left_expr = []
        for expr in bexpr.expression[0:index]:
            if isinstance(expr, AExpr):
                for sub_expr in expr.expression:
                    left_expr.append(sub_expr)
            else:
                left_expr.append(expr)
        left = AExpr(left_expr)
        if len(left.expression) == 1:
            self.left = left
        else:
            self.left = Operation(left)
        right_expr = []
        for expr in bexpr.expression[index+1:]:
            if isinstance(expr, AExpr):
                for sub_expr in expr.expression:
                    right_expr.append(sub_expr)
            else:
                right_expr.append(expr)
        right = AExpr(right_expr)
        if len(right.expression) == 1:
            self.right = right
        else:
            self.right = Operation(right)


class Operation:
    """An object representing an arithmetic operation between two variables."""
    right: Union["Operation", "AbstractExpr"]
    left: Union["Operation", "AbstractExpr"]
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
    expression: List[Union[AExpr, VariableAccess, str]]

    def __init__(self, expression: List[Union[AExpr, VariableAccess, str]]) -> None:
        self.expression = []
        for expr in expression:
            self.expression.append(expr)
        if len(self.expression) > 0:
            self.operation = BooleanOperation(self)

    def copy(self) -> "BExpr":
        """Deep copy of an expression."""
        new_expr = []
        for expr in self.expression:
            new = expr
            if isinstance(expr, VariableAccess):
                new = expr.copy()
            new_expr.append(new)
        return BExpr(new_expr)
