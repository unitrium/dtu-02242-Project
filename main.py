from Analysis.worklist import compute_reverse_post_order
from Analysis.utils import display_assignment
from Parser import ProgramGraph
from Analysis import solve_chaotic_iteration, ReachingDefintionAnalysis, LiveVariableAnalysis

program = "if (a < 2) {write a;} read a; if (b==2) {write x;} write R.fst; A[a+1]:= 0 + a - c;"

pg = ProgramGraph(program)
assignement = solve_chaotic_iteration(pg, LiveVariableAnalysis)
display_assignment(assignement)
# t, rP = compute_reverse_post_order(pg)
# print(rP)
# print(t)
