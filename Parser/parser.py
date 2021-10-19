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
            | if
            | else
            | while
            | read
            | write
    if: "if ("b_expr") {" statement "}"
    else: "if ("b_expr") {" statement "} else {"statement"}"
    while: "while ("b_expr") {" statement "}"
    read: "read " access";"
    write: "write " access";"
    array_access: variable "["(access | NUMBER)"]"
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
          | not
    not: "not" b_expr
    a_expr: a_expr opa a_expr
        | access
        | NUMBER
    opa: add
            | sub
            | mul
            | div
            | mod
    add : "+"
    sub: "-"
    mul: "*"
    div: "/"
    mod: "%"
    opb: and
        | or
    and: "&"
    or: "|"
    opr: inf
        | infe
        | sup
        | supe
        | eq
        | neq
    inf: "<"
    infe: "<="
    sup: ">"
    supe: ">="
    eq: "=="
    neq: "!="
""", start="program")
