
def display_assignment(aa: dict):
    for node_number, abs_mapping in sorted(aa.items(), key=lambda item: item[0]):
        print(f"Node {node_number}")
        for var_type, mapping in abs_mapping.items():
            print(var_type)
            print(mapping)
