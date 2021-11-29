from typing import Set

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


def mul_sign(left_sign: Set[str], right_sign: Set[str]) -> Set[str]:
    if handle_nul(left_sign, right_sign) is not None:
        return handle_nul(left_sign, right_sign)
    result = handle_undef(left_sign, right_sign)
    left_sign = left_sign - {"undef"}
    right_sign = right_sign - {"undef"}
    if left_sign == {"+", "0", "-"} or right_sign == {"+", "0", "-"}:
        return result.union({"+", "0", "-"})
    if left_sign == {"0"} or right_sign == {"0"}:
        return result.union({"0"})
    if "0" in left_sign or "0" in right_sign:
        result.add("0")
    if "-" in left_sign and "-" in right_sign and "+" in left_sign and "+" in right_sign:
        result.add("+")
    if "-" in left_sign and "+" in right_sign and "+" in left_sign and "-" in right_sign:
        result.add("-")
    return result


def div_sign(left_sign: Set[str], right_sign: Set[str]) -> Set[str]:
    if handle_nul(left_sign, right_sign) is not None:
        return handle_nul(left_sign, right_sign)
    result = handle_undef(left_sign, right_sign)
    if "0" in right_sign:
        result.add("undef")
    result.union(mul_sign(left_sign, right_sign))
    return result - set("0")


def mod_sign(left_sign: Set[str], right_sign: Set[str]) -> Set[str]:
    if handle_nul(left_sign, right_sign) is not None:
        return handle_nul(left_sign, right_sign)
    result = handle_undef(left_sign, right_sign)
    left_sign = left_sign - {"undef"}
    right_sign = right_sign - {"undef"}
    if "0" in right_sign:
        result.add("undef")
    if right_sign == {"0"}:
        return result
    result.add("0")
    if left_sign == {"0"}:
        return result
    if "-" in left_sign:
        result.add("+")
    if "+" in left_sign and "+" in right_sign:
        result.add("+")
    if "-" in left_sign and "-" in right_sign:
        result.add("-")
    if "+" in left_sign and "-" in right_sign:
        result.add("-")
    if "-" in left_sign and "+" in right_sign:
        result.add("+")
    return result


def add_sign(left_sign: Set[str], right_sign: Set[str]) -> Set[str]:
    if handle_nul(left_sign, right_sign) is not None:
        return handle_nul(left_sign, right_sign)
    result = handle_undef(left_sign, right_sign)
    left_sign = left_sign - {"undef"}
    right_sign = right_sign - {"undef"}
    if left_sign == {"+", "0", "-"} or right_sign == {"+", "0", "-"}:
        return result.union({"+", "0", "-"})
    if left_sign == {"0"}:
        return result.union(right_sign)
    if right_sign == {"0"}:
        return result.union(left_sign)
    difference = (right_sign + left_sign -
                  right_sign.intersection(left_sign)) - set("undef")
    if len(difference) == 0:
        if "0" in right_sign:
            return result.union(right_sign - {"0"})
        return result.union(right_sign)
    if "0" in difference:
        return result.union(right_sign - {"0"})
    return result.union({"+", "0", "-"})


def negation(sign: Set[str]) -> Set[str]:
    """Returns the negation of a sign set."""
    if handle_nul(sign) is not None:
        return handle_nul(sign)
    result = handle_undef(sign)
    sign = sign - {"undef"}
    if sign == {"+", "0", "-"}:
        return result.union({"+", "0", "-"})
    if "0" in sign:
        if "+" in sign:
            return result.union({"0", "-"})
        return result.union({"0", "+"})
    return result.union({"0", "-"})


def handle_nul(left: Set[str], right: Set[str] = set()) -> Set[str]:
    if len(left) == 0 or len(right) == 0:
        return set()


def handle_undef(left: Set[str], right: Set[str] = set()) -> Set[str]:
    if "undef" in left or "undef" in right:
        return set("undef")
    return set()


def sub_sign(left_sign: Set[str], right_sign: Set[str]) -> Set[str]:
    return add_sign(left_sign, negation(right_sign))
