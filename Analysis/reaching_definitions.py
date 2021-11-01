from Parser import Node, Edge, Action, POSSIBLE_ACTIONS


def kill_rd(action: Action, src_node: Node, tar_node: Node):
    if action.action_type == "assign_var" or action.action_type == "read":
        return "all"
    return None


def gen_rd(action: Action, scr_node: Node, tar_node: Node):
    if action.action_type == "assign_var" or action.action_type == "assign_arr" or action.action_type == "assign_rec" or "read":
        return (action.variables[0][0], scr_node, tar_node)
    return None


def generate_constrains(edge):
    pass
