from typing import List, Set, Tuple
from Parser import ProgramGraph
from Parser.program_graph import Node
from .abstract_analysis import AbstractAnalysis
from .reversePostorder import sort_rp, compute_reverse_post_order


class Worklist:
    currentNodes: List[Node]
    pendingNodes: Set[Node]

    def __init__(self):
        self.currentNodes = []
        self.pendingNodes = set()

    def is_empty(self) -> bool:
        return len(self.currentNodes) == 0 and len(self.pendingNodes) == 0


class AbstractSolverAlgorithm:
    def __init__(self, programGraph: ProgramGraph) -> "AbstractSolverAlgorithm":
        pass

    def insert(self, node: Node, worklist: Worklist) -> None:
        pass

    def empty(self) -> Worklist:
        return Worklist()

    def extract(self, worklist: Worklist) -> Node:
        return worklist.currentNodes.pop(0)


class RoundRobinAlgorithm(AbstractSolverAlgorithm):
    rP: dict

    def __init__(self, programGraph: ProgramGraph) -> "AbstractSolverAlgorithm":
        _, self.rP = compute_reverse_post_order(programGraph)

    def insert(self, node: Node, worklist: Worklist) -> None:
        if node not in set(worklist.currentNodes):
            worklist.pendingNodes.add(node)

    def extract(self, worklist: Worklist) -> Node:
        if len(worklist.currentNodes) == 0:
            vrp = sort_rp(list(worklist.pendingNodes), self.rP)
            q = vrp.pop(0)
            worklist.currentNodes = vrp
            worklist.pendingNodes = set()
            return q
        return worklist.currentNodes.pop(0)


class FIFOSolverAlgorithm(AbstractSolverAlgorithm):
    def insert(self, node: Node, worklist: Worklist) -> None:
        worklist.currentNodes.append(node)


class LIFOSolverAlgorithm(AbstractSolverAlgorithm):
    def insert(self, node: Node, worklist: Worklist) -> None:
        worklist.currentNodes.insert(0, node)


def worklist(prgmGraph: ProgramGraph, analysis: AbstractAnalysis, algorithmClass: AbstractSolverAlgorithm) -> Tuple[dict, int]:
    """Runs the worklist algorithm. Returns the resulting assignment and the number of steps required to reach it."""
    algorithm: AbstractSolverAlgorithm = algorithmClass(prgmGraph)
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
    while not worklist.is_empty():
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
                    test = analysis.merge(
                        s_q0, aa[edge.end.number])
                    aa[edge.end.number] = analysis.merge(
                        s_q0, aa[edge.end.number])
                    algorithm.insert(edge.end, worklist)
        steps += 1
    return aa, steps
