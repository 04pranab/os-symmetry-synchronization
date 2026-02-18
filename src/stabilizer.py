"""
stabilizer.py
-------------
Computes the stabilizer subgroup of S_n with respect to a fixed point.

Models mutual exclusion as a stabilizer subgroup constraint:
    Stab(x) = { σ ∈ S_n | σ(x) = x }

Verifies:
    - Stab(x) is a subgroup of S_n
    - |Stab(x)| = (n-1)!
    - Orbit-Stabilizer theorem: |S_n| = |Orb(x)| * |Stab(x)|
    - Coset decomposition of S_n by Stab(x)

Depends on: permutations.py
"""

import math
from src.permutations import (
    generate_Sn,
    identity,
    compose,
    inverse,
    cycle_notation_str,
    is_subgroup,
    print_group,
)



# Stabilizer Computation


def compute_stabilizer(Sn: list, fixed_point: int) -> list:
    """
    Compute the stabilizer of fixed_point in S_n.

    Stab(x) = { σ ∈ S_n | σ(x) = x }

    Args:
        Sn:          list of all permutations in S_n (from generate_Sn)
        fixed_point: the element x ∈ {1, ..., n} to stabilize

    Returns:
        List of permutations fixing fixed_point.
    """
    return [sigma for sigma in Sn if sigma[fixed_point] == fixed_point]



# Orbit Computation


def compute_orbit(Sn: list, point: int) -> set:
    """
    Compute the orbit of a point under the action of S_n.

    Orb(x) = { σ(x) | σ ∈ S_n }

    For the natural action of S_n on {1, ..., n},
    the orbit of any point is the entire set.
    """
    return {sigma[point] for sigma in Sn}



# Coset Decomposition


def left_coset(sigma: dict, subgroup: list) -> list:
    """
    Compute the left coset σ·H = { σ ∘ h | h ∈ H }.

    Args:
        sigma:    a permutation (coset representative)
        subgroup: list of permutations forming the subgroup H

    Returns:
        List of permutations in the coset σ·H.
    """
    return [compose(sigma, h) for h in subgroup]


def coset_decomposition(Sn: list, subgroup: list) -> list:
    """
    Decompose S_n into distinct left cosets of subgroup H.

    S_n = H  ∪  σ₁H  ∪  σ₂H  ∪  ...

    Returns:
        List of cosets, each coset is a list of permutations.
        The first coset is always H itself.
    """
    covered = set()
    cosets  = []

    def perm_key(sigma):
        return tuple(sorted(sigma.items()))

    subgroup_keys = {perm_key(h) for h in subgroup}

    for sigma in Sn:
        key = perm_key(sigma)
        if key not in covered:
            coset = left_coset(sigma, subgroup)
            cosets.append(coset)
            for element in coset:
                covered.add(perm_key(element))

    # Put the subgroup itself (identity coset) first
    cosets.sort(key=lambda c: 0 if perm_key(c[0]) in subgroup_keys else 1)

    return cosets



# Verification


def verify_stabilizer(n: int, fixed_point: int, verbose: bool = True) -> bool:
    """
    Full verification of the mutex–stabilizer correspondence for given n.

    Checks:
        1. Stab(x) is a valid subgroup of S_n
        2. |Stab(x)| = (n-1)!
        3. Orbit-Stabilizer: |S_n| = |Orb(x)| * |Stab(x)|
        4. Index [S_n : Stab(x)] = n
        5. Coset decomposition covers all of S_n

    Returns:
        True if all checks pass.
    """
    Sn   = generate_Sn(n)
    stab = compute_stabilizer(Sn, fixed_point)
    orb  = compute_orbit(Sn, fixed_point)

    if verbose:
        print(f"\n{'='*55}")
        print(f"Stabilizer Verification  —  n = {n},  x = {fixed_point}")
        print(f"{'='*55}")

    results = []

    # 1. Subgroup axioms
    sub_check = is_subgroup(stab, n)
    results.append(sub_check)
    if verbose:
        status = "✓" if sub_check else "✗"
        print(f"  [{status}] Stab({fixed_point}) is a subgroup of S_{n}")

    # 2. Order
    expected_order = math.factorial(n - 1)
    order_check    = len(stab) == expected_order
    results.append(order_check)
    if verbose:
        status = "✓" if order_check else "✗"
        print(f"  [{status}] |Stab({fixed_point})| = {len(stab)}  "
              f"(expected {expected_order} = ({n}-1)!)")

    # 3. Orbit-Stabilizer theorem
    os_check = len(Sn) == len(orb) * len(stab)
    results.append(os_check)
    if verbose:
        status = "✓" if os_check else "✗"
        print(f"  [{status}] Orbit-Stabilizer: |S_{n}| = |Orb| × |Stab|  →  "
              f"{len(Sn)} = {len(orb)} × {len(stab)}")

    # 4. Index
    index       = len(Sn) // len(stab)
    index_check = index == n
    results.append(index_check)
    if verbose:
        status = "✓" if index_check else "✗"
        print(f"  [{status}] Index [S_{n} : Stab({fixed_point})] = {index}  (expected {n})")

    # 5. Coset decomposition
    cosets       = coset_decomposition(Sn, stab)
    coset_check  = (len(cosets) == n and
                    sum(len(c) for c in cosets) == len(Sn))
    results.append(coset_check)
    if verbose:
        status = "✓" if coset_check else "✗"
        print(f"  [{status}] Coset decomposition: {len(cosets)} cosets × "
              f"{len(stab)} elements = {len(Sn)}")

    return all(results)



# Display Utilities


def print_cosets(n: int, fixed_point: int) -> None:
    """
    Print the full coset decomposition of S_n by Stab(fixed_point),
    with OS interpretation of each coset.
    """
    Sn     = generate_Sn(n)
    stab   = compute_stabilizer(Sn, fixed_point)
    cosets = coset_decomposition(Sn, stab)

    print(f"\nCoset decomposition of S_{n} by Stab({fixed_point}):\n")

    for idx, coset in enumerate(cosets):
        if idx == 0:
            label = f"Stab({fixed_point})       ← admissible (mutex respected)"
        else:
            # Find which process occupies the critical slot in this coset
            rep     = coset[0]
            occupant = rep[fixed_point]
            label   = f"coset {idx}  ← VIOLATION: process {occupant} in slot {fixed_point}"

        elements = ",  ".join(cycle_notation_str(s) for s in coset)
        print(f"  {label}")
        print(f"    {{ {elements} }}\n")



# Quick Verification


if __name__ == "__main__":
    print("Stabilizer Subgroup — Mutual Exclusion Verification\n")

    all_passed = True
    for n in range(2, 7):
        passed = verify_stabilizer(n, fixed_point=1, verbose=True)
        all_passed = all_passed and passed

    print(f"\n{'='*55}")
    if all_passed:
        print("All verifications passed. ✓")
    else:
        print("Some verifications FAILED. ✗")

    # Coset decomposition example for n=3
    print("\n")
    print_cosets(n=3, fixed_point=1)