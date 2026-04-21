"""
belief_base.py — Belief Base with partial meet contraction and expansion

Priority-ordered belief base:
  - Each formula has an integer priority (higher = more entrenched / more trusted).
  - Contraction uses partial meet contraction: find maximal subsets not entailing φ,
    select via priority-based selection function, take intersection.
  - Expansion simply adds the formula (with a given priority).
  - Revision = contraction by ~φ followed by expansion by φ  (Levi identity).

AGM postulates are satisfied by design:
  K1  Closure      — belief base closed under Cn (we use entailment checks)
  K-1 Success      — after B - φ, B - φ does not entail φ  (unless ⊢ φ)
  K-2 Inclusion    — B - φ ⊆ B
  K-3 Vacuity      — if B does not entail φ, then B - φ = B
  K-4 Consistency  — B - φ is consistent if B is consistent
  K-5 Extensionality — if φ ≡ ψ then B - φ = B - ψ
"""

from __future__ import annotations
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass, field
from formula import Formula, parse, is_contradiction, formulas_equivalent
from resolution import entails, is_consistent_set


@dataclass
class BeliefEntry:
    formula: Formula
    priority: int   # higher = more entrenched

    def __repr__(self):
        return f"[{self.priority}] {self.formula}"


class BeliefBase:
    """
    A prioritised belief base supporting:
      - add(φ, priority)   — expansion
      - contract(φ)        — partial meet contraction
      - revise(φ, priority)— Levi identity: contract(~φ) then expand(φ)
    """

    def __init__(self):
        self.beliefs: List[BeliefEntry] = []

    # ── Accessors ──────────────────────────────────────────────

    def formulas(self) -> List[Formula]:
        return [b.formula for b in self.beliefs]

    def is_empty(self) -> bool:
        return len(self.beliefs) == 0

    def entails(self, phi: Formula) -> bool:
        """Does the belief base logically entail φ?"""
        return entails(self.formulas(), phi)

    def is_consistent(self) -> bool:
        if self.is_empty():
            return True
        return is_consistent_set(self.formulas())

    def __repr__(self):
        if not self.beliefs:
            return "BeliefBase(∅)"
        lines = "\n".join(f"  {e}" for e in sorted(self.beliefs, key=lambda x: -x.priority))
        return f"BeliefBase(\n{lines}\n)"

    def display(self) -> str:
        if not self.beliefs:
            return "  (empty)"
        rows = sorted(self.beliefs, key=lambda x: -x.priority)
        lines = [f"  priority={e.priority:3d}  {e.formula}" for e in rows]
        return "\n".join(lines)

    # ── Expansion (K + φ) ──────────────────────────────────────

    def expand(self, phi: Formula, priority: int = 5) -> "BeliefBase":
        """
        Expansion: K + φ
        Add φ to the belief base. Does not remove anything.
        Returns a new BeliefBase.
        """
        new_bb = self._copy()
        # If formula already present, update priority
        for entry in new_bb.beliefs:
            if formulas_equivalent(entry.formula, phi):
                entry.priority = max(entry.priority, priority)
                return new_bb
        new_bb.beliefs.append(BeliefEntry(phi, priority))
        return new_bb

    # ── Contraction (K ÷ φ) ────────────────────────────────────

    def contract(self, phi: Formula) -> "BeliefBase":
        """
        Partial Meet Contraction: K ÷ φ
        
        Algorithm:
          1. If K does not entail φ, return K unchanged (Vacuity).
          2. Compute all maximal subsets of K that do NOT entail φ.
          3. Apply the priority-based selection function γ:
             select the subset(s) with highest total priority.
          4. Return the intersection of selected subsets.

        Satisfies AGM postulates K-1 through K-5.
        """
        # Vacuity: if we don't believe φ, nothing to do
        if not self.entails(phi):
            return self._copy()

        # If φ is a tautology, contraction has no effect (can't remove it)
        if _is_tautology_formula(phi):
            return self._copy()

        formulas = self.formulas()
        n = len(formulas)

        # Generate all maximal subsets not entailing φ
        remainders = _maximal_subsets_not_entailing(formulas, phi)

        if not remainders:
            # Only possible if every individual formula entails φ alone
            # Return empty base
            return BeliefBase()

        # Selection function: pick remainder(s) with highest priority score
        # Priority score = sum of priorities of included formulas
        priority_map = {i: self.beliefs[i].priority for i in range(n)}
        scored = [(sum(priority_map[i] for i in rem), rem) for rem in remainders]
        best_score = max(s for s, _ in scored)
        selected = [rem for s, rem in scored if s == best_score]

        # Intersection of selected remainders
        if not selected:
            intersection = set()
        else:
            intersection = set(selected[0])
            for rem in selected[1:]:
                intersection &= set(rem)

        new_bb = BeliefBase()
        for idx in intersection:
            new_bb.beliefs.append(BeliefEntry(self.beliefs[idx].formula, self.beliefs[idx].priority))
        return new_bb

    # ── Revision (K * φ) — Levi Identity ──────────────────────

    def revise(self, phi: Formula, priority: int = 5) -> "BeliefBase":
        """
        Revision: K * φ  =  (K ÷ ¬φ) + φ   [Levi identity]

        Satisfies AGM revision postulates.
        """
        from formula import Neg
        neg_phi = Neg(phi)
        contracted = self.contract(neg_phi)
        return contracted.expand(phi, priority)

    # ── Internal helpers ───────────────────────────────────────

    def _copy(self) -> "BeliefBase":
        new_bb = BeliefBase()
        new_bb.beliefs = [BeliefEntry(e.formula, e.priority) for e in self.beliefs]
        return new_bb


# ─────────────────────────────────────────────────────────────
#  Remainder computation (maximal subsets not entailing φ)
# ─────────────────────────────────────────────────────────────

def _maximal_subsets_not_entailing(formulas: List[Formula], phi: Formula) -> List[List[int]]:
    """
    Compute K ⊥ φ: all maximal subsets of `formulas` (by index) that do not entail φ.
    Uses a bottom-up search.
    """
    n = len(formulas)
    if n == 0:
        return []

    # Check each formula individually — if φ is a tautology nothing helps
    # We'll collect subsets represented as frozensets of indices

    remainders: List[List[int]] = []

    def is_entailing(indices):
        return entails([formulas[i] for i in indices], phi)

    # BFS/DFS: start from full set and remove minimal elements
    # Efficient approach: iterate over all subsets of size n-1, n-2, ...
    # But for tractability use the upward-closed / downward-closed property:
    # K ⊥ φ is an antichain in the power set.

    # We use a recursive approach: find maximal non-entailing subsets
    _find_remainders(list(range(n)), formulas, phi, remainders, set())

    # Remove dominated subsets (keep only maximal ones)
    maximal = []
    for rem in remainders:
        rem_set = frozenset(rem)
        dominated = any(
            rem_set < frozenset(other) for other in remainders
        )
        if not dominated:
            maximal.append(rem)

    # Deduplicate
    seen = set()
    result = []
    for rem in maximal:
        key = frozenset(rem)
        if key not in seen:
            seen.add(key)
            result.append(list(sorted(rem)))

    return result


def _find_remainders(
    candidates: List[int],
    formulas: List[Formula],
    phi: Formula,
    remainders: List[List[int]],
    current: frozenset,
):
    """
    Recursive helper: try adding each candidate; track maximal non-entailing subsets.
    """
    # If adding any candidate would entail φ, record current as a remainder
    extended = False
    for idx in candidates:
        test = list(current | {idx})
        if not entails([formulas[i] for i in test], phi):
            # Safe to add: recurse
            new_candidates = [c for c in candidates if c > idx]
            _find_remainders(new_candidates, formulas, phi, remainders, current | {idx})
            extended = True

    if not extended:
        # Can't extend without entailing φ — current is maximal
        if not entails([formulas[i] for i in current], phi):
            remainders.append(list(current))


def _is_tautology_formula(phi: Formula) -> bool:
    """Quick tautology check via resolution."""
    from formula import Neg
    from resolution import pl_resolution, formula_to_clauses
    neg_clauses = formula_to_clauses(Neg(phi))
    return pl_resolution(neg_clauses)
