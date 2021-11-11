from typing import Dict, List
from Analysis.abstract_analysis import AbstractAnalysis
from Analysis.reaching_definitions import ReachingDefintionAnalysis
from Parser import Node, Edge, Action, POSSIBLE_ACTIONS
from Parser.program_graph import ProgramGraph


class LiveVariableAnalysis(ReachingDefintionAnalysis):
    @staticmethod
    def update_mapping(mapping: Dict, edge: Edge) -> Dict:
        """Update the mapping based on the kill/gen functions of the analysis."""
        new_mapping = ReachingDefintionAnalysis.copy_mapping(mapping)
        if edge.action.action_type == "assign_var" or edge.action.action_type == "read":
            new_mapping["variable"][edge.action.variables[0]] = {
                f"{edge.start.number},{edge.end.number}"}
        elif edge.action.action_type == "assign_arr":
            new_mapping["array"][edge.action.variables[0]] = new_mapping["array"][edge.action.variables[0][0]].add(
                f"{edge.start.number},{edge.end.number}")
        elif edge.action.action_type == "assign_rec":
            new_mapping["record"][edge.action.variables[0]] = new_mapping["record"][edge.action.variables[0][0]].add(
                f"{edge.start.number},{edge.end.number}")
        return new_mapping
