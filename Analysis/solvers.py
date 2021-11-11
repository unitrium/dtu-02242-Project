from Parser import ProgramGraph
from .abstract_analysis import AbstractAnalysis


def solve_chaotic_iteration(programGraph: ProgramGraph, analysis: AbstractAnalysis):
    aa = {}
    for node in programGraph.get_nodes():
        aa[node.number] = "undef"
    aa[0] = analysis.init_mapping(programGraph)
    edges = programGraph.get_edges()
    while len(edges) > 0:
        edge = edges.pop(0)
        s_q0 = analysis.update_mapping(aa[edge.start.number], edge)
        if not analysis.included(mapping1=s_q0, mapping2=aa[edge.end.number]):
            aa[edge.end.number] = analysis.merge(s_q0, aa[edge.end.number])
    return aa
