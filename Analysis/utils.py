

def copy_mapping(mapping: dict):
    new = {}
    for var_type, variables in mapping.items():
        for var in variables:
            new[var_type][var] = [pair for pair in var.values()]
    return new
