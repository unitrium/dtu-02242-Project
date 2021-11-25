from os import stat
from typing import Dict, Set
from Parser import Edge, POSSIBLE_ACTIONS, ProgramGraph
from Parser.struc_elements import Operation

from .reaching_definitions import ReachingDefintionAnalysis
from .abstract_analysis import AbstractAnalysis


class SignDetectionAnalysis(ReachingDefintionAnalysis):
    @staticmethod
    def init_mapping(programGraph: ProgramGraph) -> Dict:
        """Initializes the mapping according to the analysis."""
        assignment = {
            "variable": {},
            "array": {},
            "record": {}
        }
        for var_type, variables in programGraph.variables.items():
            for var in variables.keys():
                assignment[var_type][var] = {"+", "0", "-"}
        return assignment

    @staticmethod
    def copy_mapping(mapping: Dict) -> Dict:
        """Returns a deep copy of a mapping."""
        return ReachingDefintionAnalysis.copy_mapping(mapping)

    @staticmethod
    def update_mapping(mapping: Dict, edge: Edge) -> Dict:
        if AbstractAnalysis.update_mapping(mapping, edge) is not None:
            return AbstractAnalysis.update_mapping(mapping, edge)
        new_mapping = ReachingDefintionAnalysis.copy_mapping(mapping)
        if edge.action.action_type == "assign":
            new_sign = {"+", "0", "-"}
            # case we are directly coping from another var or int.
            if not edge.action.right_expression.operation:
                variable = edge.action.right_expression.expression[0]
                # this is an integer.
                if isinstance(variable, str):
                    new_sign = sign(int(variable))
                # this is another var.
                else:
                    new_sign = mapping[edge.action.variable.variable_type][variable]
            # case we need to explore the arithmetic expression to get the sign.
            else:
                new_sign = reccursive_sign(
                    edge.action.right_expression.operation, mapping)
            new_mapping[edge.action.variable.variable_type][edge.action.variable.name] = new_sign
        return new_mapping

    @staticmethod
    def merge(mapping1: Dict, mapping2: Dict) -> Dict:
        """Merge two mappings."""
        return ReachingDefintionAnalysis.merge(mapping1, mapping2)

    @staticmethod
    def included(mapping1: Dict, mapping2: Dict) -> bool:
        """Checks if the mapping1 is included in the mapping 2."""
        return ReachingDefintionAnalysis.included(mapping1, mapping2)


def reccursive_sign(operation: Operation, mapping: Dict) -> Set[str]:
    if isinstance(operation.right, Operation):
        right_sign = reccursive_sign(operation.right, mapping)
    else:
        if isinstance(operation.right.expression[0], str):
            right_sign = sign(int(operation.right.expression[0]))
        else:
            right_sign = mapping[operation.right.expression[0]
                                 .variable_type][operation.right.expression[0].name]
    if isinstance(operation.left, Operation):
        left_sign = reccursive_sign(operation.left, mapping)
    else:
        if isinstance(operation.left.expression[0], str):
            left_sign = sign(int(operation.left.expression[0]))
        else:
            left_sign = mapping[operation.left.expression[0]
                                .variable_type][operation.left.expression[0].name]
    if operation.operator == "*" or operation.operator == "/":
        return mul_sign(left_sign, right_sign)
    elif operation.operator == "+":
        return add_sign(left_sign, right_sign)
    elif operation.operator == "-":
        return sub_sign(left_sign, right_sign)


def mul_sign(left_sign: Set[str], right_sign: Set[str]) -> Set[str]:
    if len(left_sign) == 0 or len(right_sign) == 0:
        return set()
    if left_sign == {"+", "0", "-"} or right_sign == {"+", "0", "-"}:
        return {"+", "0", "-"}
    if left_sign == {"0"} or right_sign == {"0"}:
        return {"0"}
    result = set()
    if "0" in left_sign or "0" in right_sign:
        result.add("0")
    if "-" in left_sign and "-" in right_sign and "+" in left_sign and "+" in right_sign:
        result.add("+")
    if "-" in left_sign and "+" in right_sign and "+" in left_sign and "-" in right_sign:
        result.add("-")
    return result


def add_sign(left_sign: Set[str], right_sign: Set[str]) -> Set[str]:
    if len(left_sign) == 0 or len(right_sign) == 0:
        return set()
    if left_sign == {"+", "0", "-"} or right_sign == {"+", "0", "-"}:
        return {"+", "0", "-"}
    if left_sign == {"0"}:
        return right_sign
    if right_sign == {"0"}:
        return left_sign
    difference = right_sign + left_sign - right_sign.intersection(left_sign)
    if len(difference) == 0:
        if "0" in right_sign:
            return right_sign - {"0"}
        return right_sign
    if "0" in difference:
        return right_sign - {"0"}
    return {"+", "0", "-"}


def negation(sign: Set[str]) -> Set[str]:
    """Returns the negation of a sign set."""
    if len(sign) == 0:
        return set()
    if len(sign) == 3:
        return {"+", "0", "-"}
    if "0" in sign:
        if "+" in sign:
            return {"0", "-"}
        return {"0", "+"}
    return {"0", "-"}


def sub_sign(left_sign: Set[str], right_sign: Set[str]) -> Set[str]:
    return add_sign(left_sign, negation(right_sign))


def sign(n: int) -> Set[str]:
    if n > 0:
        return {"+"}
    elif n < 0:
        return {"-"}
    return {"0"}
