from typing import Callable, Set

"""Relational operators."""


def greater_than(left: str, right: str, strict: bool = False) -> set:
    """Implementation of abstract > or >= if strict is enabled."""
    result = set()
    if left == "+":
        result.add("tt")
        if right == "+":
            result.add("ff")
    elif left == "-":
        result.add("ff")
        if right == "-":
            result.add("tt")
    # left is 0
    else:
        if right == "-":
            result.add("tt")
        else:
            result.add("ff")
            if not strict:
                result.add("tt")
    return result


def equal(left: str, right: str) -> set:
    """Implementation of abstract ==."""
    if left == "0" and right == "0":
        return set("tt")
    if left == right:
        return set(["tt", "ff"])
    return set("ff")


"""Bolean operators."""


def not_sign(signs: Set[str]) -> Set[str]:
    """Given a set of signs gives the boolean negation."""
    return {"+", "0", "-"} - signs


"""Arithmetic operators."""


def handle_null_undef(left: Set[str], right: Set[str]) -> Set[str]:
    if len(left) == 0 or len(right) == 0:
        return set()
    if "undef" in left or "undef" in right:
        return set("undef")


def mul_sign(left: Set[str], right: Set[str]) -> Set[str]:
    """Abstract multiplication for set of one element"""
    if handle_null_undef(left, right) is not None:
        return handle_null_undef(left, right)
    if "0" in left or "0" in right:
        return set("0")
    if left == right:
        return set("+")
    return set("-")


def div_sign(left: Set[str], right: Set[str]) -> Set[str]:
    if handle_null_undef(left, right) is not None:
        return handle_null_undef(left, right)
    if "0" in right:
        return set("undef")
    return mul_sign(left, right)


def add_sign(left: Set[str], right: Set[str]) -> Set[str]:
    if handle_null_undef(left, right) is not None:
        return handle_null_undef(left, right)
    if "0" in left:
        return set([key for key in right])
    if "0" in right:
        return set([key for key in left])
    if left == right:
        return set([key for key in left])
    else:
        return set(["+", "0", "-"])


def sub_sign(left: Set[str], right: Set[str]) -> Set[str]:
    if handle_null_undef(left, right) is not None:
        return handle_null_undef(left, right)
    return add_sign(left, negation_sign(right))


def negation_sign(right: Set[str]) -> Set[str]:
    """Negates a set of one sign."""
    if len(right) == 0:
        return set()
    if "undef" in right:
        return set("undef")
    if "+" in right:
        return set("-")
    elif "-" in right:
        return set("+")
    else:
        return set("0")


def mod_sign(left: Set[str], right: Set[str]) -> Set[str]:
    if handle_null_undef(left, right) is not None:
        return handle_null_undef(left, right)
    if "0" in right:
        return set("undef")
    if "0" in left:
        return set("0")
    if "+" in left and "+" in right:
        return set(["+", "0"])
    if "+" in left and "-" in right:
        return set(["-", "0"])
    if "-" in left and "+" in right:
        return set(["+", "0"])
    else:
        return set(["-", "0"])


def abstract_arithmetic(left: Set[str], right: Set[str], fct: Callable) -> Set[str]:
    if len(left) == 0 or len(right) == 0:
        return set()
    result = set()
    for left_sign in left:
        for right_sign in right:
            for key in fct(left_sign, right_sign):
                result.add(key)
    return result


def negation(sign: Set[str]) -> Set[str]:
    """Returns the negation of a sign set."""
    if len(sign) == 0:
        return set()
    result = set("undef") if "undef" in sign else set()
    if "0" in sign:
        result.union({"0"})
    if "-" in sign:
        result.union({"+"})
    if "+" in sign:
        result.union({"-"})
    return result
