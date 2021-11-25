from Analysis.solvers import FIFOSolverAlgorithm, LIFOSolverAlgorithm, RoundRobinAlgorithm
from Analysis.reversePostorder import compute_reverse_post_order
from Analysis.utils import display_assignment
from Parser import ProgramGraph
from Analysis import ReachingDefintionAnalysis, LiveVariableAnalysis, worklist, SignDetectionAnalysis

program = "int[3] A; int a; int b; int c; int x; {int fst; int snd} R; if (a < 2) {write a;} read a; if (b==2) {write x;} write R.fst; A[a+1]:= 0 + a - c;"

pg = ProgramGraph(program)
assignment, steps = worklist(
    pg, LiveVariableAnalysis, RoundRobinAlgorithm)
print(steps)
# display_assignment(assignment)
