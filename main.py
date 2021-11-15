from Analysis.solvers import FIFOSolverAlgorithm, LIFOSolverAlgorithm
from Analysis.reversePostorder import compute_reverse_post_order
from Analysis.utils import display_assignment
from Parser import ProgramGraph
from Analysis import solve_chaotic_iteration, ReachingDefintionAnalysis, LiveVariableAnalysis, worklist

program = "if (a < 2) {write a;} read a; if (b==2) {write x;} write R.fst; A[a+1]:= 0 + a - c;"

pg = ProgramGraph(program)
#assignment = solve_chaotic_iteration(pg, LiveVariableAnalysis)
assignment, steps = worklist(
    pg, LiveVariableAnalysis, FIFOSolverAlgorithm)
display_assignment(assignment)
print(steps)
# t, rP = compute_reverse_post_order(pg)
# print(rP)
# print(t)
