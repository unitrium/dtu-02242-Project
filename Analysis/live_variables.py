from typing import Dict, List
from Analysis.abstract_analysis import AbstractAnalysis
from Analysis.reaching_definitions import ReachingDefintionAnalysis
from Parser import Node, Edge, Action, POSSIBLE_ACTIONS
from Parser.program_graph import ProgramGraph
# from .utils import copy_mapping

class LiveVar(AbstractAnalysis):
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



"""
def generate_constrains_LV(edges: List[Edge], all_variables):
    # assignment = init_reaching_definition_assignment(all_variables)
    constraints = {
        # 0: assignment
    }
    for edge in edges:
        if edge.start.number in constraints.keys():
            constraints[edge.start.number] = merge_rd_assignment(constraints[edge.start.number], update_mapping_rd(mapping=constraints[edge.end.number],
                                                                                                                   action=edge.action, src_node=edge.start, dst_node=edge.end))
        else:
            constraints[edge.start.number] = update_mapping_rd(mapping=constraints[edge.end.number],
                                                               action=edge.action, src_node=edge.start, dst_node=edge.end)
    return constraints
"""