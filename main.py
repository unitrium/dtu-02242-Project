from Analysis.worklist import compute_reverse_post_order
from Analysis.utils import display_assignment
from Parser import ProgramGraph
from Analysis import solve_chaotic_iteration, ReachingDefintionAnalysis

program = "if (a < 2) {write a;} read a; if (b==2) {write x;} write R.fst; A[a]:= 0;"

pg = ProgramGraph(program)
assignement = solve_chaotic_iteration(pg, ReachingDefintionAnalysis)
display_assignment(assignement)
t, rP = compute_reverse_post_order(pg)
# print(rP)
# print(t)
