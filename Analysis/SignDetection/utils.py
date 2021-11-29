from typing import Set


def sign(n: int) -> Set[str]:
    if n > 0:
        return {"+"}
    elif n < 0:
        return {"-"}
    return {"0"}
