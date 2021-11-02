from Parser.parser import grammar
from Parser.program_graph import high_level_edges, check_edges, get_all_variables

program = "if (a < 2) {write a;} read a; if (b==2) {write x;} write R.fst; A[a]:= 0;"
tree = grammar.parse(program)

edges, init_node = high_level_edges(tree)
variables = {
    "variable": set(),
    "array": set(),
    "record": set()
}
get_all_variables(tree, variables)
print(variables)
check_edges(edges)
for edge in edges:
    print(edge)
