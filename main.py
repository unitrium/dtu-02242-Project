from Parser.parser import grammar
from Parser.program_graph import high_level_edges, Node

program = "if (a < 2) {write a;} read a; if (b==2) {write x;}"
tree = grammar.parse(program)
print(tree.children)

edges = high_level_edges(tree)
for edge in edges:
    print(edge)
