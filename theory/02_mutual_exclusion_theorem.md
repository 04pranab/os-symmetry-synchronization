# 02 — Mutual Exclusion as a Stabilizer Subgroup

## Formalizing the Mutex Constraint

This document develops Claim 2: that mutual exclusion corresponds to restricting the admissible scheduling space to a stabilizer subgroup of `S_n`.

Prerequisites: definitions from `01_formal_model.md` — symmetric group, subgroup, group action, stabilizer.

---

## 1. The Problem in OS Terms

In a system with `n` processes, mutual exclusion (mutex) is the requirement that at most one process occupies a **critical section** at any time. Operationally this is enforced by locks, semaphores, or monitors.

The question this project asks is: *what does this constraint look like as a restriction on the scheduling space `S_n`?*

---

## 2. Modelling the Critical Section

We model the critical section as a designated process slot — a specific position in the execution order that only one process may occupy at a time.

More precisely, fix an element `x ∈ P`. Think of `x` as the **protected resource slot**. A schedule `σ ∈ S_n` **respects the mutex constraint on `x`** if it does not move `x` — that is, if the process assigned to slot `x` remains `x` itself:

```
σ respects mutex on x  ⟺  σ(x) = x
```

This is exactly the fixed-point condition.

**Definition 2.1 (Mutex-Admissible Schedules).** Given a critical resource represented by `x ∈ P`, the set of mutex-admissible schedules is:

```
M(x) = { σ ∈ S_n | σ(x) = x }
```

---

## 3. M(x) is a Stabilizer Subgroup

**Theorem 3.1.** `M(x) = Stab_{S_n}(x)`, and `M(x)` is a subgroup of `S_n`.

*Proof.*

The equality `M(x) = Stab(x)` is immediate from the definitions — both are defined as the set of permutations fixing `x`.

To verify `M(x) ≤ S_n`, we check the three subgroup conditions:

**Identity:** `e(x) = x`, so `e ∈ M(x)`. ✓

**Closure:** Let `σ, τ ∈ M(x)`, so `σ(x) = x` and `τ(x) = x`. Then:
```
(σ ∘ τ)(x) = σ(τ(x)) = σ(x) = x
```
So `σ ∘ τ ∈ M(x)`. ✓

**Inverses:** Let `σ ∈ M(x)`, so `σ(x) = x`. Applying `σ⁻¹` to both sides:
```
σ⁻¹(σ(x)) = σ⁻¹(x)  ⟹  x = σ⁻¹(x)
```
So `σ⁻¹ ∈ M(x)`. ✓

Therefore `M(x)` is a subgroup of `S_n`. ∎

---

## 4. The Order of M(x)

**Theorem 4.1.** `|M(x)| = (n-1)!`

*Proof.*

By the Orbit-Stabilizer theorem:

```
|S_n| = |Orb(x)| × |Stab(x)|
```

The orbit of any element `x ∈ P` under the natural action of `S_n` is all of `P`, since for any `y ∈ P` there exists a permutation mapping `x` to `y`. Therefore `|Orb(x)| = n`.

Substituting:

```
n! = n × |Stab(x)|  ⟹  |Stab(x)| = (n-1)!
```

Alternatively: a permutation fixing `x` is free to permute the remaining `n-1` elements in any order. There are exactly `(n-1)!` such permutations. 

---

## 5. Structural Interpretation

The index of `M(x)` in `S_n` is:

```
[S_n : M(x)] = |S_n| / |M(x)| = n! / (n-1)! = n
```

This says the stabilizer subgroup partitions `S_n` into exactly `n` cosets. Each coset corresponds to a distinct assignment of which process occupies the critical slot — there are `n` such choices, one per process.

The mutex constraint selects exactly **one** of these cosets: the one where slot `x` is occupied by process `x` itself. The remaining `n-1` cosets are the schedules where some other process has taken the critical slot — precisely the schedules that violate mutual exclusion.

This gives a clean coset picture of mutex:

```
S_n = M(x)  ∪  σ₁M(x)  ∪  σ₂M(x)  ∪  ...  ∪  σ_{n-1}M(x)
       ↑              ↑
  admissible      inadmissible (mutex violation)
```

---

## 6. Worked Example — n = 3, x = 1

From `S_3 = { e, (12), (13), (23), (123), (132) }`, the schedules fixing process `1` are:

```
M(1) = { σ ∈ S_3 | σ(1) = 1 }
     = { e, (23) }
```

Verification:
- `e(1) = 1` ✓
- `(23)(1) = 1` ✓  (this permutation only swaps 2 and 3, leaving 1 fixed)
- `(12)(1) = 2` ✗
- `(13)(1) = 3` ✗
- `(123)(1) = 2` ✗
- `(132)(1) = 3` ✗

So `|M(1)| = 2 = (3-1)!` ✓

The cosets of `M(1)` in `S_3`:

```
M(1)       = { e,     (23)  }   ← process 1 holds the resource (admissible)
(12)·M(1)  = { (12),  (132) }   ← process 2 holds the resource (violation)
(13)·M(1)  = { (13),  (123) }   ← process 3 holds the resource (violation)
```

---

## 7. Isomorphism of M(x)

**Proposition 7.1.** `M(x) ≅ S_{n-1}`

*Proof sketch.* Any permutation in `M(x)` fixes `x` and acts as a bijection on the remaining `n-1` elements `P \ {x}`. This action is itself a permutation of `n-1` elements, so there is a natural isomorphism between `M(x)` and `S_{n-1}`. ∎

This is consistent with `|M(x)| = (n-1)! = |S_{n-1}|`.

---

## 8. Summary

| Property | Value |
|----------|-------|
| Definition | `M(x) = { σ ∈ S_n | σ(x) = x }` |
| Algebraic object | Stabilizer subgroup `Stab_{S_n}(x)` |
| Order | `(n-1)!` |
| Index in `S_n` | `n` |
| Isomorphic to | `S_{n-1}` |
| OS interpretation | Schedules respecting mutex on resource `x` |

---

## 9. Computational Verification

The source file `src/stabilizer.py` implements this directly:

1. Generate all of `S_n`
2. Filter for permutations satisfying `σ(x) = x`
3. Verify the result is a subgroup (check identity, closure, inverses)
4. Check `|M(x)| = (n-1)!`
5. Check Lagrange: `|M(x)|` divides `n!`

See also: `notebooks/02_compute_stabilizer.ipynb` for an interactive walkthrough.

---

*Previous: [01 — Formal Model](01_formal_model.md)*  
*Next: [03 — Round-Robin Scheduling as a Cyclic Subgroup](03_cyclic_scheduling.md)*