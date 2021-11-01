from Parser.parser import grammar
from Parser.program_graph import high_level_edges, check_edges

program = "if (a < 2) {write a;} read a; if (b==2) {write x;}"
tree = grammar.parse(program)

edges, init_node = high_level_edges(tree)
check_edges(edges)
for edge in edges:
    print(edge)
