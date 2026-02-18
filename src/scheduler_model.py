"""
scheduler_model.py
------------------
Unified scheduling model that ties all four claims together.

Provides a single interface to:
    - Represent and query the full scheduling space S_n
    - Check mutex admissibility (stabilizer subgroup)
    - Check round-robin admissibility (cyclic subgroup)
    - Detect deadlock (identity element)
    - Run the full verification suite across all claims

This is the top-level module. All group-theoretic work is
delegated to permutations.py, stabilizer.py, and cyclic_group.py.

Depends on: permutations.py, stabilizer.py, cyclic_group.py
"""

import math
from permutations import (
    generate_Sn,
    identity,
    compose,
    cycle_notation_str,
    is_subgroup,
    print_group,
)
from stabilizer import (
    compute_stabilizer,
    verify_stabilizer,
    print_cosets,
)
from cyclic_group import (
    generate_cyclic_subgroup,
    make_n_cycle,
    verify_cyclic_subgroup,
    print_cyclic_subgroup,
)



# Scheduler Model


class SchedulerModel:
    """
    Represents the scheduling space for n processes as S_n,
    with methods to query synchronization constraints.

    Attributes:
        n      : number of processes
        Sn     : list of all permutations in S_n
        stab   : stabilizer subgroup Stab(1) — mutex-admissible schedules
        cyclic : cyclic subgroup ⟨c⟩ — round-robin schedules
        e      : identity permutation — deadlock state
    """

    def __init__(self, n: int):
        if n < 2:
            raise ValueError("Need at least 2 processes (n ≥ 2).")
        self.n      = n
        self.Sn     = generate_Sn(n)
        self.e      = identity(n)
        self.stab   = compute_stabilizer(self.Sn, fixed_point=1)
        self.cyclic = generate_cyclic_subgroup(n)

   
    # Claim 1 — Full Scheduling Space
   

    def scheduling_space_size(self) -> int:
        """Return |S_n| = n!"""
        return len(self.Sn)

    def all_schedules(self) -> list:
        """Return all n! schedules."""
        return self.Sn

   
    # Claim 2 — Mutual Exclusion
   

    def is_mutex_admissible(self, sigma: dict, critical_slot: int = 1) -> bool:
        """
        Check whether schedule sigma respects mutual exclusion on critical_slot.

        A schedule is mutex-admissible iff sigma(critical_slot) = critical_slot,
        i.e., the process assigned to the critical slot does not change.

        Args:
            sigma:         a permutation dict
            critical_slot: the protected resource slot (default 1)

        Returns:
            True if sigma ∈ Stab(critical_slot).
        """
        return sigma[critical_slot] == critical_slot

    def mutex_admissible_schedules(self, critical_slot: int = 1) -> list:
        """Return all schedules admissible under mutex on critical_slot."""
        return compute_stabilizer(self.Sn, critical_slot)

   
    # Claim 3 — Round-Robin
   

    def is_round_robin(self, sigma: dict) -> bool:
        """
        Check whether schedule sigma is a valid round-robin schedule.

        A schedule is round-robin iff sigma ∈ ⟨c⟩.

        Returns:
            True if sigma is a rotation of the process queue.
        """
        cyclic_keys = [tuple(sorted(s.items())) for s in self.cyclic]
        return tuple(sorted(sigma.items())) in cyclic_keys

    def round_robin_schedules(self) -> list:
        """Return all n round-robin schedules."""
        return self.cyclic

   
    # Claim 4 — Deadlock
   

    def is_deadlock(self, sigma: dict) -> bool:
        """
        Check whether schedule sigma represents a deadlocked system.

        Deadlock iff sigma = e (identity permutation).
        No process makes forward progress.

        Returns:
            True if sigma is the identity element.
        """
        return sigma == self.e

    def deadlock_state(self) -> dict:
        """Return the deadlock state — the identity permutation."""
        return self.e

   
    # Schedule Classification
   

    def classify(self, sigma: dict) -> dict:
        """
        Classify a schedule by which constraints it satisfies.

        Returns a dict with keys:
            'permutation'   : cycle notation string
            'is_deadlock'   : bool
            'is_mutex'      : bool  (w.r.t. slot 1)
            'is_round_robin': bool
        """
        return {
            "permutation"    : cycle_notation_str(sigma),
            "is_deadlock"    : self.is_deadlock(sigma),
            "is_mutex"       : self.is_mutex_admissible(sigma),
            "is_round_robin" : self.is_round_robin(sigma),
        }

    def classify_all(self) -> list:
        """Classify every schedule in S_n."""
        return [self.classify(sigma) for sigma in self.Sn]

   
    # Display
   

    def summary(self) -> None:
        """Print a structural summary of the scheduling model."""
        print(f"\n{'='*60}")
        print(f"  Scheduler Model  —  n = {self.n} processes")
        print(f"{'='*60}")
        print(f"  Full space  S_{self.n}         : {len(self.Sn)} schedules  "
              f"({self.n}! = {math.factorial(self.n)})")
        print(f"  Mutex space Stab(1)      : {len(self.stab)} schedules  "
              f"(({self.n}-1)! = {math.factorial(self.n - 1)})")
        print(f"  Round-robin ⟨c⟩          : {len(self.cyclic)} schedules  "
              f"(|Z_{self.n}| = {self.n})")
        print(f"  Deadlock    {{e}}           : 1 schedule")
        print(f"\n  Subgroup chain:  {{e}} ≤ ⟨c⟩ ≤ S_{self.n}")
        print(f"                   {{e}} ≤ Stab(1) ≤ S_{self.n}")

    def print_classification_table(self) -> None:
        """Print a table classifying all schedules in S_n."""
        classifications = self.classify_all()

        print(f"\nClassification of all schedules in S_{self.n}:\n")
        print(f"  {'Permutation':<20} {'Deadlock':<12} {'Mutex':<12} {'Round-Robin'}")
        print(f"  {'-'*18} {'-'*10} {'-'*10} {'-'*11}")

        for c in classifications:
            dl  = "yes" if c["is_deadlock"]    else "-"
            mx  = "yes" if c["is_mutex"]       else "-"
            rr  = "yes" if c["is_round_robin"] else "-"
            print(f"  {c['permutation']:<20} {dl:<12} {mx:<12} {rr}")



# Full Verification Suite


def run_full_verification(n_values: list = None, verbose: bool = True) -> None:
    """
    Run all four claim verifications for each value of n.

    Args:
        n_values: list of n to verify (default: [2, 3, 4, 5, 6])
        verbose:  print detailed output per check
    """
    if n_values is None:
        n_values = [2, 3, 4, 5, 6]

    print("=" * 60)
    print("  OS Synchronization as Symmetry Restrictions in S_n")
    print("=" * 60)

    all_passed = True

    for n in n_values:

        # Claim 1
        Sn = generate_Sn(n)
        c1 = len(Sn) == math.factorial(n)

        # Claim 2
        c2 = verify_stabilizer(n, fixed_point=1, verbose=verbose)

        # Claim 3
        c3 = verify_cyclic_subgroup(n, verbose=verbose)

        # Claim 4 — identity is unique fixed element
        e        = identity(n)
        fixall   = [s for s in Sn if all(s[i] == i for i in range(1, n + 1))]
        c4       = (len(fixall) == 1 and fixall[0] == e)

        passed = c1 and c2 and c3 and c4
        all_passed = all_passed and passed

        if verbose:
            print(f"\n  Claim 1 — |S_{n}| = {n}! = {math.factorial(n)}: "
                  f"{'✓' if c1 else '✗'}")
            print(f"  Claim 4 — unique identity in S_{n}:  "
                  f"{'✓' if c4 else '✗'}")

    print(f"\n{'='*60}")
    if all_passed:
        print("  All claims verified for n ∈ "
              f"{n_values}  ✓")
    else:
        print("  Some verifications FAILED.  ✗")
    print("=" * 60)



# Quick Demo


if __name__ == "__main__":

    # Full verification across all n
    run_full_verification(verbose=False)

    # Structural summary for n=4
    model = SchedulerModel(n=4)
    model.summary()

    # Classification table for n=3 (small enough to print fully)
    model3 = SchedulerModel(n=3)
    model3.print_classification_table()

    # Coset decomposition for n=3 (mutex violations)
    print()
    print_cosets(n=3, fixed_point=1)

    # Round-robin schedules for n=4
    print_cyclic_subgroup(n=4)

    # Demonstrate individual checks
    print("\nIndividual schedule checks (n=3):\n")
    Sn3 = generate_Sn(3)
    for sigma in Sn3:
        c = model3.classify(sigma)
        flags = []
        if c["is_deadlock"]    : flags.append("DEADLOCK")
        if c["is_mutex"]       : flags.append("mutex-ok")
        if c["is_round_robin"] : flags.append("round-robin")
        flag_str = ", ".join(flags) if flags else "unconstrained"
        print(f"  {c['permutation']:<15}  {flag_str}")