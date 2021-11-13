from Parser import ProgramGraph
from .abstract_analysis import AbstractAnalysis
from random import randint


def solve_chaotic_iteration(programGraph: ProgramGraph, analysis: AbstractAnalysis):
    aa = {}
    for node in programGraph.get_nodes():
        aa[node.number] = "undef"
    first_node = 0
    if analysis.reverse():
        first_node = programGraph.get_last_node().number
    aa[first_node] = analysis.init_mapping(programGraph)
    edges = programGraph.get_edges()
    while len(edges) > 0:
        index = randint(0, len(edges)-1)
        edge = edges[index]
        if analysis.reverse():
            if not aa[edge.end.number] == "undef":
                s_q0 = analysis.update_mapping(aa[edge.end.number], edge)
                if not analysis.included(mapping1=s_q0, mapping2=aa[edge.start.number]):
                    aa[edge.start.number] = analysis.merge(
                        s_q0, aa[edge.start.number])
                else:
                    edges.pop(index)
        else:
            if not aa[edge.start.number] == "undef":
                s_q0 = analysis.update_mapping(aa[edge.start.number], edge)
                if not analysis.included(mapping1=s_q0, mapping2=aa[edge.end.number]):
                    aa[edge.end.number] = analysis.merge(
                        s_q0, aa[edge.end.number])
                else:
                    edges.pop(index)
    return aa
