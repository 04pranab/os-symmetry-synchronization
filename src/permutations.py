"""
permutations.py
---------------
Core implementation of the symmetric group S_n.

Generates all permutations of n processes, implements composition,
inversion, cycle notation, and basic group-theoretic checks.

All permutations are represented as Python dicts:
    { 1: σ(1), 2: σ(2), ..., n: σ(n) }

Example:
    σ = {1: 2, 2: 3, 3: 1}  represents the 3-cycle (1 2 3)
"""

from itertools import permutations as _itertools_permutations



# Representation


def make_permutation(mapping: dict) -> dict:
    """
    Construct a permutation from a plain dict and validate it.

    Args:
        mapping: dict of the form {1: σ(1), 2: σ(2), ..., n: σ(n)}

    Returns:
        The same dict if it is a valid permutation.

    Raises:
        ValueError if the mapping is not a bijection.
    """
    keys = set(mapping.keys())
    values = set(mapping.values())
    if keys != values:
        raise ValueError(
            f"Not a valid permutation: domain {keys} != codomain {values}"
        )
    return dict(mapping)


def identity(n: int) -> dict:
    """
    Return the identity permutation on {1, ..., n}.

    e(i) = i for all i.
    """
    return {i: i for i in range(1, n + 1)}



# Group Operations


def compose(sigma: dict, tau: dict) -> dict:
    """
    Compose two permutations: (sigma ∘ tau)(i) = sigma(tau(i)).

    Applies tau first, then sigma.

    Args:
        sigma: outer permutation
        tau:   inner permutation

    Returns:
        The composed permutation as a dict.
    """
    if set(sigma.keys()) != set(tau.keys()):
        raise ValueError("Permutations must be defined on the same set.")
    return {i: sigma[tau[i]] for i in tau}


def inverse(sigma: dict) -> dict:
    """
    Return the inverse permutation σ⁻¹.

    σ⁻¹(σ(i)) = i  for all i.
    """
    return {v: k for k, v in sigma.items()}


def power(sigma: dict, k: int) -> dict:
    """
    Return σ^k (sigma composed with itself k times).

    Handles:
        k > 0  : repeated composition
        k = 0  : identity
        k < 0  : repeated composition of inverse
    """
    n = len(sigma)
    result = identity(n)

    if k == 0:
        return result

    base = sigma if k > 0 else inverse(sigma)
    for _ in range(abs(k)):
        result = compose(result, base)

    return result


def order(sigma: dict) -> int:
    """
    Return the order of a permutation — the smallest k > 0 such that σ^k = e.
    """
    n = len(sigma)
    e = identity(n)
    current = dict(sigma)
    k = 1
    while current != e:
        current = compose(current, sigma)
        k += 1
    return k



# Generating S_n


def generate_Sn(n: int) -> list:
    """
    Generate all n! elements of the symmetric group S_n.

    Returns:
        List of permutations, each a dict {1: ..., 2: ..., ..., n: ...}.
    """
    elements = []
    for perm in _itertools_permutations(range(1, n + 1)):
        elements.append(dict(zip(range(1, n + 1), perm)))
    return elements



# Cycle Notation


def to_cycles(sigma: dict) -> list:
    """
    Convert a permutation to its cycle decomposition.

    Returns:
        List of tuples, each tuple is one cycle.
        The identity is returned as [].

    Example:
        sigma = {1: 2, 2: 3, 3: 1, 4: 4}
        to_cycles(sigma) → [(1, 2, 3)]
    """
    visited = set()
    cycles = []

    for start in sorted(sigma.keys()):
        if start in visited:
            continue
        cycle = []
        current = start
        while current not in visited:
            visited.add(current)
            cycle.append(current)
            current = sigma[current]
        if len(cycle) > 1:
            cycles.append(tuple(cycle))

    return cycles


def cycle_notation_str(sigma: dict) -> str:
    """
    Return a human-readable cycle notation string.

    Example:
        {1: 2, 2: 3, 3: 1} → "(1 2 3)"
        identity            → "e"
    """
    cycles = to_cycles(sigma)
    if not cycles:
        return "e"
    return "".join(f"({' '.join(str(x) for x in c)})" for c in cycles)



# Subgroup Verification


def is_subgroup(subset: list, n: int) -> bool:
    """
    Check whether a list of permutations forms a subgroup of S_n.

    Verifies:
        1. Identity is present
        2. Closed under composition
        3. Closed under inverses

    Args:
        subset: list of permutation dicts
        n:      number of processes

    Returns:
        True if subset is a subgroup, False otherwise.
    """
    e = identity(n)
    subset_set = [tuple(sorted(s.items())) for s in subset]

    # 1. Identity
    if tuple(sorted(e.items())) not in subset_set:
        print("  [FAIL] Identity not in subset.")
        return False

    # 2. Closure
    for s in subset:
        for t in subset:
            st = compose(s, t)
            if tuple(sorted(st.items())) not in subset_set:
                print(f"  [FAIL] Not closed: {cycle_notation_str(s)} ∘ "
                      f"{cycle_notation_str(t)} = {cycle_notation_str(st)} not in subset.")
                return False

    # 3. Inverses
    for s in subset:
        inv_s = inverse(s)
        if tuple(sorted(inv_s.items())) not in subset_set:
            print(f"  [FAIL] Inverse of {cycle_notation_str(s)} not in subset.")
            return False

    return True



# Display Utilities


def print_group(group: list, label: str = "Group") -> None:
    """Print all elements of a group in cycle notation."""
    print(f"{label}  (order {len(group)}):")
    for sigma in group:
        print(f"  {cycle_notation_str(sigma)}  →  {list(sigma.values())}")



# Quick Verification


if __name__ == "__main__":
    for n in range(2, 7):
        Sn = generate_Sn(n)
        e  = identity(n)
        assert len(Sn) == __import__('math').factorial(n), f"|S_{n}| should be {n}!"
        assert is_subgroup(Sn, n), f"S_{n} should be a subgroup of itself"
        print(f"S_{n}:  |S_{n}| = {len(Sn)}  ✓")

    print("\nS_3 elements:")
    print_group(generate_Sn(3), "S_3")

    print("\nComposition check: (1 2) ∘ (2 3) in S_3")
    s1 = {1: 2, 2: 1, 3: 3}   # (1 2)
    s2 = {1: 1, 2: 3, 3: 2}   # (2 3)
    result = compose(s1, s2)
    print(f"  (1 2) ∘ (2 3) = {cycle_notation_str(result)}")

    print("\nOrder check:")
    c = {1: 2, 2: 3, 3: 4, 4: 1}   # (1 2 3 4)
    print(f"  order of (1 2 3 4) = {order(c)}   (expected 4)")