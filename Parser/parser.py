"""Takes an array of token and creates the abstract syntax tree resulting."""
from lark import Lark

grammar = Lark(r"""
    program: (statement | declaration)*
    declaration: "int" variable";"
                | "int["NUMBER"] " variable";"
                | "{int fst; int snd} " variable";"
    statement: assignment
            | "if ("b_expr") {" statement "}"
            | "if ("b_expr") {" statement "} else {"statement"}"
            | "while ("b_expr") {" statement "}"
            | "read " variable";"
            | "write " variable";"
    ?value: NUMBER
    | array
    | record

    b_expr: "true" -> true
          | "false" -> false
          | a_expr opr a_expr
          | b_expr opb b_expr
          | "not " b_expr
    a_expr: a_expr opa a_expr
        | value
    opa: "+"
            | "-"
            | "*"
            | "/"
            | "%"
    opb: "&"
        | "|"
    opr: "<"
        | ">"
        | "<="
        | ">="
        | "=="
        | "!="
    assignment: variable ":="value";"
    variable: CNAME
    array: "[" [value ("," value)*] "]"
    record: "(" value "," value ")"
    %import common.SIGNED_NUMBER -> NUMBER
    %import common.ESCAPED_STRING -> STRING
    %import common.CNAME -> CNAME
    %import common.WS
    %ignore WS
""", start="program")
