from typing import Dict, List
from Parser import Node, Edge, Action, POSSIBLE_ACTIONS
from .utils import copy_mapping


def update_mapping_rd(mapping: dict, action: Action, src_node: Node, dst_node: Node):
    new_mapping = copy_mapping(mapping)
    if action.action_type == "assign_var" or action.action_type == "read":
        new_mapping["variable"][action.variables[0]] = {
            f"{src_node.number},{dst_node.number}"}
    elif action.action_type == "assign_arr":
        new_mapping["array"][action.variables[0]] = new_mapping["array"][action.variables[0]].add(
            f"{src_node.number},{dst_node.number}")
    elif action.action_type == "assign_rec":
        new_mapping["record"][action.variables[0]] = new_mapping["record"][action.variables[0]].add(
            f"{src_node.number},{dst_node.number}")
    return new_mapping


def init_reaching_definition_assignment(all_variables: Dict) -> Dict:
    assignment = {}
    for var_type, variables in all_variables.items():
        for var in variables:
            assignment[var_type][var] = {"?,0"}
    return assignment


def merge_rd_assignment(matching1: dict, matching2: dict) -> dict:
    new_matching = copy_mapping(matching1)
    for var_type, variables in matching2.items():
        for var in variables.keys():
            for pair in var.values():
                new_matching[var_type][var].add(pair)
    return new_matching


def generate_constrains(edges: List[Edge], all_variables):
    assignment = init_reaching_definition_assignment(all_variables)
    constraints = {
        0: assignment
    }
    for edge in edges:
        if edge.end.number in constraints.keys():
            constraints[edge.end.number] = merge_rd_assignment(constraints[edge.end.number], update_mapping_rd(mapping=constraints[edge.start.number],
                                                                                                               action=edge.action, src_node=edge.start, dst_node=edge.end))
        else:
            constraints[edge.end.number] = update_mapping_rd(mapping=constraints[edge.start.number],
                                                             action=edge.action, src_node=edge.start, dst_node=edge.end)
    return constraints
