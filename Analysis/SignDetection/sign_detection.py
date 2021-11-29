from typing import Dict, List, Set, Tuple, Union
from Parser import Edge, POSSIBLE_ACTIONS, ProgramGraph
from Parser.struc_elements import VALID_A_OPERATORS, VALID_B_OPERATORS, VALID_R_OPERATORS, AExpr, BooleanOperation, Operation, VariableAccess

from ..reaching_definitions import ReachingDefintionAnalysis
from ..abstract_analysis import AbstractAnalysis

from .abstract_sign_operators import *
from .utils import sign


class SignDetectionMapping:
    """Structure to represent a mapping."""
    variable: Dict[str, Set[str]]
    array: Dict[str, List[Set[str]]]
    record: Dict[str, List[Set[str]]]

    def __init__(self, programGraph: ProgramGraph = None) -> None:
        self.array = {}
        self.record = {}
        self.variable = {}
        if programGraph is not None:
            for var_type, variables in programGraph.variables.items():
                for var in variables.keys():
                    if var_type == "array":
                        self.array[var] = set()
                    elif var_type == "record":
                        self.record[var] = [
                            set()] * 2
                    else:
                        self.variable[var] = set()

    def get_result(self, variable: VariableAccess):
        if variable.variable_type == "variable":
            return self.variable[variable.name]
        if variable.variable_type == "array":
            return self.array[variable.name]
        if variable.variable_type == "record":
            return self.record[variable.name]

    def set_result(self, value: Set[str], variable: VariableAccess):
        if variable.variable_type == "variable":
            self.variable[variable.name] = value
        elif variable.variable_type == "record":
            if variable.rec_type == "fst":
                self.record[variable.name][0] = value
            else:
                self.record[variable.name][1] = value
        elif variable.variable_type == "array":
            # TODO Finish array
            self.array[variable.name] = value

    def copy(self) -> "SignDetectionMapping":
        """Returns a deep copy of the mapping."""
        newMapping = SignDetectionMapping()
        for var_name, signs in self.variable.items():
            newSet = set([sign for sign in signs])
            newMapping.variable[var_name] = newSet
        for var_name, signs in self.record.items():
            for i in range(len(signs)):
                if var_name not in newMapping.record:
                    newMapping.record[var_name] = []
                newSet = set([sign for sign in signs[i]])
                newMapping.record[var_name].append(newSet)
        for var_name, signs in self.array.items():
            if var_name not in newMapping.array:
                newMapping.array[var_name] = set([sign for sign in signs])
        return newMapping

    def __str__(self) -> str:
        return f"Variables: \n {self.variable} \n Arrays: \n {self.array} Records: \n {self.record}"


class SignDetectionAnalysis(ReachingDefintionAnalysis):
    @staticmethod
    def init_mapping(programGraph: ProgramGraph) -> SignDetectionMapping:
        """Initializes the mapping according to the analysis."""
        return SignDetectionMapping(programGraph)

    @staticmethod
    def update_mapping(mapping: SignDetectionMapping, edge: Edge) -> SignDetectionMapping:
        if AbstractAnalysis.update_mapping(mapping, edge) is not None:
            return AbstractAnalysis.update_mapping(mapping, edge)
        new_mapping = mapping.copy()
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
                    new_sign = mapping.get_result(
                        variable)
            # case we need to explore the arithmetic expression to get the sign.
            else:
                new_sign = reccursive_sign(
                    edge.action.right_expression.operation, mapping)
            if edge.action.variable.variable_type == "variable":
                new_mapping.variable[edge.action.variable.name] = new_sign
            elif edge.action.variable.variable_type == "record":
                if edge.action.variable.rec_type == "fst":
                    new_mapping.record[edge.action.variable.name][0] = new_sign
                else:
                    new_mapping.record[edge.action.variable.name][1] = new_sign
            else:
                index_sign = reccursive_sign(
                    edge.action.variable.child_accesses, mapping)
                if len(index_sign) == 0:
                    new_mapping.array[edge.action.variable.name] = set()
                else:
                    new_mapping.array[edge.action.variable.name] = new_sign
        if edge.action.action_type == "boolean":
            return reccursive_boolean_sign(edge.action.right_expression.operation, new_mapping)
        return new_mapping

    @staticmethod
    def merge(mapping1: SignDetectionMapping, mapping2: SignDetectionMapping) -> SignDetectionMapping:
        """Merge two mappings."""
        merge = AbstractAnalysis.merge(mapping1, mapping2)
        if merge is not None:
            return merge.copy()
        new_mapping = mapping1.copy()
        for var_name, signs in mapping2.variable.items():
            new_mapping.variable[var_name] = new_mapping.variable[var_name].union(
                signs)
        for var_name, signs in mapping2.record.items():
            for index, _ in enumerate(new_mapping.record[var_name]):
                new_mapping.record[var_name][index] = new_mapping.record[var_name][index].union(
                    mapping2.record[var_name][index])
        for var_name, signs in mapping2.array.items():
            for index, _ in enumerate(new_mapping.array[var_name]):
                new_mapping.array[var_name][index] = new_mapping.array[var_name][index].union(
                    mapping2.array[var_name][index])
        return new_mapping

    @staticmethod
    def included(mapping1: SignDetectionMapping, mapping2: SignDetectionMapping) -> bool:
        """Checks if the mapping1 is included in the mapping 2."""
        undef = AbstractAnalysis.included(mapping1, mapping2)
        if undef is not None:
            return undef
        for var_name, signs in mapping1.variable.items():
            for sign in signs:
                if sign not in mapping2.variable[var_name]:
                    return False
        for var_name, signList in mapping1.record.items():
            for index, signs in enumerate(signList):
                for sign in signs:
                    if sign not in mapping2.record[var_name][index]:
                        return False
        for var_name, signList in mapping1.array.items():
            for index, signs in enumerate(signList):
                for sign in signs:
                    if sign not in mapping2.array[var_name][index]:
                        return False
        return True


def reccursive_sign(operation: Union[Operation, AExpr], mapping: SignDetectionMapping) -> Set[str]:
    """Given an operation or an arithmetic exprresion extracts the sign."""
    if isinstance(operation, AExpr):
        if len(operation.expression) > 1:
            return reccursive_sign(operation.operation, mapping)
        variable = operation.expression[0]
        # This is a direct int.
        if isinstance(variable, str):
            return sign(int(variable))
        return mapping.get_result(variable)
    if isinstance(operation.right, Operation):
        right_sign = reccursive_sign(operation.right, mapping)
    else:
        if isinstance(operation.right.expression[0], str):
            right_sign = sign(int(operation.right.expression[0]))
        else:
            right_sign = mapping.get_result(operation.right.expression[0])
    if isinstance(operation.left, Operation):
        left_sign = reccursive_sign(operation.left, mapping)
    else:
        if isinstance(operation.left.expression[0], str):
            left_sign = sign(int(operation.left.expression[0]))
        else:
            left_sign = mapping.get_result(operation.left.expression[0])
    if operation.operator == "*":
        fct = mul_sign
    elif operation.operator == "/":
        fct = div_sign
    elif operation.operator == "%":
        fct = mod_sign
    elif operation.operator == "+":
        fct = add_sign
    elif operation.operator == "-":
        fct = sub_sign
    return abstract_arithmetic(left_sign, right_sign, fct)


def reccursive_boolean_sign(operation: BooleanOperation, mapping: SignDetectionMapping) -> SignDetectionMapping:
    """Get the sign of a boolean, returns a mapping that has been updated with the new knowledge."""
    new_mapping = mapping.copy()
    # Breaking down the boolean expression.
    if not operation.is_relational():
        if operation.operator in ["&", "|"]:
            return merge_bool(operation.operator, reccursive_boolean_sign(operation.left, new_mapping), reccursive_boolean_sign(operation.right, new_mapping))
        else:
            return merge_bool("not", reccursive_boolean_sign(operation.right, new_mapping))
    else:
        sign_left, sign_right = sign_relative_operation(
            operation, new_mapping)
        for expr in operation.left.expression:
            if isinstance(expr, VariableAccess):
                new_mapping.set_result(sign_left, expr)
        for expr in operation.right.expression:
            if isinstance(expr, VariableAccess):
                new_mapping.set_result(sign_right, expr)
        return new_mapping


def sign_relative_operation(operation: BooleanOperation, mapping: SignDetectionMapping) -> Tuple[Set[str], Set[str]]:
    """Returns the possible signs for the left and the rigth of the operation."""
    if operation.operator not in VALID_R_OPERATORS:
        raise Exception(
            f"Trying to get relative sign for a non relative operation: {operation.operator}")
    left_signs = reccursive_sign(operation.left, mapping)
    right_signs = reccursive_sign(operation.right, mapping)
    possible_right_signs = set()
    possible_left_signs = set()
    for left_sign in left_signs:
        for right_sign in right_signs:
            result = {}
            if operation.operator == ">":
                result = greater_than(left_sign, right_sign)
            elif operation.operator == ">=":
                result = greater_than(left_sign, right_sign, True)
            elif operation.operator == "<":
                result = greater_than(
                    negation(left_sign), negation(right_sign))
            elif operation.operator == "<=":
                result = greater_than(negation(left_sign),
                                      negation(right_sign), True)
            elif operation.operator == "==":
                result = equal(left_sign, right_sign)
            if "tt" in result:
                possible_right_signs.add(right_sign)
                possible_left_signs.add(left_sign)
    return possible_left_signs, possible_right_signs


def merge_bool(operator: str, left: SignDetectionMapping, right: SignDetectionMapping = None) -> SignDetectionMapping:
    """Merge two sign mapping using the specified boolean operator."""
    if operator not in VALID_B_OPERATORS:
        raise Exception(f"Unknown boolean operator: {operator}")
    new_mapping = left.copy()
    for var_name, sign in new_mapping.variable.items():
        if operator == "&":
            new_mapping.variable[var_name] = right.variable[var_name].intersection(
                sign)
        elif operator == "|":
            new_mapping.variable[var_name] = right.variable[var_name].union(
                sign)
        else:
            new_mapping.variable[var_name] = not_sign(
                (left.variable[var_name]))
    for var_name, signList in new_mapping.record.items():
        for index, signs in enumerate(signList):
            if operator == "&":
                new_mapping.record[var_name][index] = right.record[var_name][index].intersection(
                    signs)
            elif operator == "|":
                new_mapping.record[var_name][index] = right.record[var_name][index].union(
                    signs)
            else:
                new_mapping.record[var_name][index] = not_sign(
                    (left.record[var_name][index]))
    for var_name, signList in new_mapping.array.items():
        for index, signs in enumerate(signList):
            if operator == "&":
                new_mapping.array[var_name][index] = right.array[var_name][index].intersection(
                    signs)
            elif operator == "|":
                new_mapping.array[var_name][index] = right.array[var_name][index].union(
                    signs)
            else:
                new_mapping.array[var_name][index] = not_sign(
                    (left.array[var_name][index]))
    return new_mapping
