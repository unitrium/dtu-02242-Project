
from Analysis.SignDetection.sign_detection import SignDetectionMapping


def display_assignment(aa: dict):
    for node_number, abs_mapping in sorted(aa.items(), key=lambda item: item[0]):
        print(f"Node {node_number}")
        if isinstance(abs_mapping, SignDetectionMapping):
            print(abs_mapping)
        else:
            for var_type, mapping in abs_mapping.items():
                print(var_type)
                print(mapping)
