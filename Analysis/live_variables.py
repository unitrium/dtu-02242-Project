from typing import Dict, List
from Analysis.reaching_definitions import init_reaching_definition_assignment, merge_rd_assignment, update_mapping_rd
from Parser import Node, Edge, Action, POSSIBLE_ACTIONS
from .utils import copy_mapping


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
