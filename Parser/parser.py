"""Takes an array of token and creates the abstract syntax tree resulting."""
from lark import Lark

grammar = Lark(r"""
    %import common.SIGNED_NUMBER -> NUMBER
    %import common.ESCAPED_STRING -> STRING
    %import common.CNAME -> CNAME
    %import common.WS
    %ignore WS

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
    array_access: variable "["a_expr"]"
    record_fst_access: variable ".fst"
    record_snd_access: variable ".snd"
    record_access: record_fst_access
                 | record_snd_access
    access: array_access
          | record_access
          | variable
    assignment: access ":="a_expr";"
    variable: CNAME
    ?value: NUMBER
    | access
    | array
    | record

    array: "[" [value ("," value)*] "]"
    record: "(" value "," value ")"

    b_expr: "true" -> true
          | "false" -> false
          | a_expr opr a_expr
          | b_expr opb b_expr
          | "not " b_expr
    a_expr: a_expr opa a_expr
        | access
        | NUMBER
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
""", start="program")
