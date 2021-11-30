from Analysis.solvers import FIFOSolverAlgorithm, LIFOSolverAlgorithm, RoundRobinAlgorithm
from Analysis.reversePostorder import compute_reverse_post_order
from Analysis.utils import display_assignment
from Parser import ProgramGraph
from Analysis import ReachingDefintionAnalysis, LiveVariableAnalysis, worklist, SignDetectionAnalysis

#program = "int[3] A; int a; int b; int c; int x; {int fst; int snd} R; if (a < 2) {write a;} read a; if (b==2) {write x;} write R.fst; A[a+1]:= 0 + a - c;"
with open("microCCode.txt", "r") as text:
    pg = ProgramGraph(text.read())

    assignment, steps = worklist(
        pg, SignDetectionAnalysis, RoundRobinAlgorithm)

    print(steps)
    display_assignment(assignment)
