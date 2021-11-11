from typing import Dict, List
from Analysis.abstract_analysis import AbstractAnalysis
from Analysis.reaching_definitions import ReachingDefintionAnalysis
from Parser import Node, Edge, Action, POSSIBLE_ACTIONS
from Parser.program_graph import ProgramGraph


class LiveVariableAnalysis(ReachingDefintionAnalysis):
    @staticmethod
    def update_mapping(mapping: Dict, edge: Edge) -> Dict:
        """Update the mapping based on the kill/gen functions of the analysis."""
        new_mapping = LiveVariableAnalysis.copy_mapping(mapping)
        if edge.action.action_type == "assign":  # TODO also kill
            for variable in edge.action.right_expression.get_variables():
                new_mapping[edge.start.number][variable.variable_type].add(
                    variable.name)
            if edge.action.variable.variable_type == "array":
                for variable in edge.action.variable.child_accesses.get_variables():
                    new_mapping[edge.start.number][variable.variable_type].add(
                        variable.name)
        # TODO read, write, bool
        return new_mapping

    @staticmethod
    def init_mapping(programGraph: ProgramGraph) -> Dict:
        """Initializes the mapping according to the analysis."""
        assignment = {
            "variable": {},
            "array": {},
            "record": {}
        }
        for node in programGraph.nodes.values():
            assignment[node.number]["variable"] = set()
            assignment[node.number]["array"] = set()
            assignment[node.number]["record"] = set()
        return assignment
