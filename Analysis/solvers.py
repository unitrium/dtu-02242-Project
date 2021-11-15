from typing import Any, List, Tuple
from Parser import ProgramGraph
from Parser.program_graph import Edge, Node
from .abstract_analysis import AbstractAnalysis
from random import randint


class AbstractSolverAlgorithm:
    @staticmethod
    def insert(node: Node, worklist: List[Node]) -> None:
        pass

    @staticmethod
    def empty() -> List[Node]:
        return []

    @staticmethod
    def extract(worklist: List[Node]) -> Node:
        return worklist.pop(0)


class FIFOSolverAlgorithm(AbstractSolverAlgorithm):
    @staticmethod
    def insert(node: Node, worklist: List[Node]) -> None:
        worklist.append(node)


class LIFOSolverAlgorithm(AbstractSolverAlgorithm):
    @staticmethod
    def insert(node: Node, worklist: List[Node]) -> None:
        worklist.insert(0, node)


def worklist(prgmGraph: ProgramGraph, analysis: AbstractAnalysis, algorithm: AbstractSolverAlgorithm) -> Tuple[dict, int]:
    """Runs the worklist algorithm. Returns the resulting assignment and the number of steps required to reach it."""
    aa = {}
    worklist = algorithm.empty()
    for node in prgmGraph.get_nodes():
        aa[node.number] = "undef"
        algorithm.insert(node, worklist)
    first_node = 0
    if analysis.reverse():
        first_node = prgmGraph.get_last_node().number
    aa[first_node] = analysis.init_mapping(prgmGraph)
    steps = 0
    while len(worklist) != 0:
        q0 = algorithm.extract(worklist)
        if analysis.reverse():
            for edge in q0.incoming_edges:
                s_q0 = analysis.update_mapping(aa[edge.end.number], edge)
                if not analysis.included(mapping1=s_q0, mapping2=aa[edge.start.number]):
                    aa[edge.start.number] = analysis.merge(
                        s_q0, aa[edge.start.number])
                    algorithm.insert(edge.start, worklist)
        else:
            for edge in q0.outgoing_edges:
                s_q0 = analysis.update_mapping(aa[edge.start.number], edge)
                if not analysis.included(mapping1=s_q0, mapping2=aa[edge.end.number]):
                    aa[edge.end.number] = analysis.merge(
                        s_q0, aa[edge.end.number])
                    algorithm.insert(edge.end, worklist)
        steps += 1
    return aa, steps
