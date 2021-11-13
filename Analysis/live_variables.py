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
        # Gen functions
        if edge.action.action_type == "assign":
            for variable in edge.action.right_expression.get_variables():
                new_mapping[edge.start.number][variable.variable_type].add(
                    variable.name)
            if edge.action.variable.variable_type == "array":
                for variable in edge.action.variable.child_accesses.get_variables():
                    new_mapping[edge.start.number][variable.variable_type].add(
                        variable.name)
        if edge.action.action_type == "read" and edge.action.variable.variable_type == "array":
            for variable in edge.action.variable.child_accesses.get_variables():
                new_mapping[edge.start.number][variable.variable_type].add(
                    variable.name)
        if edge.action.action_type == "write":
            new_mapping[edge.start.number][edge.action.variable.variable_type].add(
                edge.action.variable.name
            )
        if edge.action.action_type == "boolean":
            for variable in edge.action.right_expression.get_variables():
                new_mapping[edge.start.number][variable.variable_type].add(
                    variable.name)
            # Kill functions for assign var and read var
        if edge.action.action_type == "assign" or edge.action.action_type == "read":
            if edge.action.variable.variable_type == "variable" and edge.action.variable.name in new_mapping[edge.start.number]["variable"]:
                new_mapping[edge.start.number]["variable"].remove(
                    edge.action.variable.name)
        return new_mapping

    @staticmethod
    def init_mapping(programGraph: ProgramGraph) -> Dict:
        """Initializes the mapping according to the analysis."""
        assignment = {
        }
        for node in programGraph.nodes.values():
            assignment[node.number] = {
                "variable": set(),
                "array": set(),
                "record": set()
            }
        return assignment

    @staticmethod
    def reverse() -> bool:
        return True

    @staticmethod
    def copy_mapping(mapping: Dict) -> Dict:
        """Returns a deep copy of a mapping."""
        new = {
        }
        for node, variables in mapping.items():
            new[node] = {}
            for var_type, liveVariables in variables.items():
                new[node][var_type] = set([var for var in liveVariables])
        return new

    @staticmethod
    def included(mapping1: Dict, mapping2: Dict) -> bool:
        """Checks if the mapping1 is included in the mapping 2."""
        undef = AbstractAnalysis.included(mapping1, mapping2)
        if undef is not None:
            return undef
        for node, mapping in mapping1.items():
            for var_type, liveVariables in mapping.items():
                for var in liveVariables:
                    if var not in mapping2[node][var_type]:
                        return False
        return True

    @staticmethod
    def merge(mapping1: Dict, mapping2: Dict) -> Dict:
        """Merge two mappings."""
        merge = AbstractAnalysis.merge(mapping1, mapping2)
        if merge is not None:
            return merge
        new_matching = LiveVariableAnalysis.copy_mapping(mapping1)
        for node, mapping in mapping2.items():
            for var_type, liveVariables in mapping.items():
                for variable in liveVariables:
                    new_matching[node][var_type].add(variable)
        return new_matching
