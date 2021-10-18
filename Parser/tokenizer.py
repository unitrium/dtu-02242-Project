"""Take a string as input and outputs an array of token in the order in which they are read."""

STATEMENTS = [":=", "if", "else", "while", "read", "write", ","]
DECLARATIONS = ["int", "int["]
ARITHMETIC_OPERATORS = ["+", "-", "*", "/", "%"]
RELATIVE_OPERATORS = ["<", ">", "<=", ">=", "==", "!="]
BOOLEAN_OPERATORS = ["&", "|", "!"]


class Token:
    value: str
    variable: bool
