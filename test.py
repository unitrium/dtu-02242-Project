from Analysis.solvers import FIFOSolverAlgorithm, LIFOSolverAlgorithm
from Analysis.reversePostorder import compute_reverse_post_order
from Analysis.utils import display_assignment
from Parser import ProgramGraph
from Analysis import solve_chaotic_iteration, ReachingDefintionAnalysis, LiveVariableAnalysis, worklist

# if even write 0 else write 1 and when odd goes to loop and writes 007.
program = "int a; a := 11; b := false; if ( a/2 == 0) { write 0; } else { b:= true; write 1; } while(b) { write 007; }"


pg = ProgramGraph(program)

assignment, steps = worklist(
    pg, LiveVariableAnalysis, FIFOSolverAlgorithm)

display_assignment(assignment)
print(steps)
