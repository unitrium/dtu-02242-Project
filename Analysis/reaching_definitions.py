from typing import Dict
from Parser import Edge, POSSIBLE_ACTIONS, ProgramGraph

from .abstract_analysis import AbstractAnalysis


class ReachingDefintionAnalysis(AbstractAnalysis):
    @staticmethod
    def merge(mapping1: Dict, mapping2: Dict) -> Dict:
        """Merge two mappings."""
        merge = AbstractAnalysis.merge(mapping1, mapping2)
        if merge is not None:
            return merge
        new_matching = ReachingDefintionAnalysis.copy_mapping(mapping1)
        for var_type, variables in mapping2.items():
            for var in variables.keys():
                for pair in var.values():
                    new_matching[var_type][var].add(pair)
        return new_matching

    @staticmethod
    def included(mapping1: Dict, mapping2: Dict) -> bool:
        """Checks if the mapping1 is included in the mapping 2."""
        undef = AbstractAnalysis.included(mapping1, mapping2)
        if undef is not None:
            return undef
        for var_type, variables in mapping1.items():
            for var, mapping in variables.items():
                for pair in mapping:
                    if pair not in mapping2[var_type][var]:
                        return False
        return True

    @staticmethod
    def init_mapping(programGraph: ProgramGraph) -> Dict:
        """Initializes the mapping according to the analysis."""
        assignment = {
            "variable": {},
            "array": {},
            "record": {}
        }
        for var_type, variables in programGraph.variables.items():
            for var in variables:
                assignment[var_type][var] = {"?,0"}
        return assignment

    @staticmethod
    def update_mapping(mapping: Dict, edge: Edge) -> Dict:
        """Update the mapping based on the kill/gen functions of the analysis."""
        new_mapping = ReachingDefintionAnalysis.copy_mapping(mapping)
        if edge.action.action_type == "assign" or edge.action.action_type == "read":
            if edge.action.variable.variable_type == "var":
                new_mapping["variable"][edge.action.variable.name] = {
                    f"{edge.start.number},{edge.end.number}"}
            elif edge.action.variable.variable_type == "arr":
                new_mapping["array"][edge.action.variable.name].add(
                    f"{edge.start.number},{edge.end.number}"
                )
            elif edge.action.action_type == "rec":
                new_mapping["record"][edge.action.variable.name].add(
                    f"{edge.start.number},{edge.end.number}"
                )
        return new_mapping

    @staticmethod
    def copy_mapping(mapping: Dict) -> Dict:
        """Returns a deep copy of a mapping."""
        new = {
            "variable": {},
            "array": {},
            "record": {}
        }
        for var_type, variables in mapping.items():
            for var, mapping in variables.items():
                new[var_type][var] = set([pair for pair in mapping])
        return new
