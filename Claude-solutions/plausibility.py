"""
plausibility.py — Plausibility order on possible worlds

A plausibility order (total preorder) ≤ on possible worlds (interpretations)
where w ≤ w' means "w is at least as plausible as w'".

Supports:
  - Logical entailment: φ is believed iff φ is true in ALL minimal worlds.
  - Lexicographic revision by φ: reorder worlds so φ-worlds come first,
    preserving relative order within each group.
  - Minimal revision (also called "restrained" or "natural" revision):
    move only the most plausible φ-worlds to the front.

The plausibility order is represented as a ranked list of equivalence classes
(ranks), where rank 0 = most plausible.
"""

from __future__ import annotations
from typing import List, Set, Dict, FrozenSet, Tuple, Optional
from formula import Formula, parse, all_interpretations, formulas_equivalent
from resolution import entails


# An interpretation is a frozenset of true atoms (atoms not in the set are false)
Interp = FrozenSet[str]   # frozenset of atoms that are TRUE


def interp_to_dict(world: Interp, all_atoms: Set[str]) -> Dict[str, bool]:
    return {a: (a in world) for a in all_atoms}


def interp_satisfies(world: Interp, phi: Formula, all_atoms: Set[str]) -> bool:
    return phi.evaluate(interp_to_dict(world, all_atoms))


def format_world(world: Interp, all_atoms: List[str]) -> str:
    parts = []
    for a in sorted(all_atoms):
        parts.append(a if a in world else f"~{a}")
    return "{" + ", ".join(parts) + "}"


class PlausibilityOrder:
    """
    A total preorder on possible worlds, represented as an ordered list of ranks.
    ranks[0] = most plausible (minimal) worlds.
    ranks[k] = worlds at level k.

    Each world is a frozenset of atom names that are TRUE in that world.
    """

    def __init__(self, atoms: Set[str], ranks: Optional[List[Set[Interp]]] = None):
        self.atoms: Set[str] = set(atoms)
        if ranks is not None:
            self.ranks: List[Set[Interp]] = ranks
        else:
            # Default: all worlds equally plausible (one rank)
            all_worlds = self._all_worlds()
            self.ranks = [all_worlds]

    def _all_worlds(self) -> Set[Interp]:
        result = set()
        for interp_dict in all_interpretations(self.atoms):
            w = frozenset(a for a, v in interp_dict.items() if v)
            result.add(w)
        return result

    def all_worlds(self) -> List[Interp]:
        worlds = []
        for rank in self.ranks:
            worlds.extend(sorted(rank))
        return worlds

    def rank_of(self, world: Interp) -> int:
        """Return the rank index of a world (0 = most plausible)."""
        for i, rank_set in enumerate(self.ranks):
            if world in rank_set:
                return i
        raise ValueError(f"World {world} not in plausibility order")

    def minimal_worlds(self) -> Set[Interp]:
        """Return the set of most plausible worlds (rank 0)."""
        for rank in self.ranks:
            if rank:
                return set(rank)
        return set()

    def minimal_phi_worlds(self, phi: Formula) -> Set[Interp]:
        """Return the most plausible worlds that satisfy φ."""
        for rank in self.ranks:
            phi_worlds = {w for w in rank if interp_satisfies(w, phi, self.atoms)}
            if phi_worlds:
                return phi_worlds
        return set()

    # ── Entailment ────────────────────────────────────────────

    def believes(self, phi: Formula) -> bool:
        """
        φ is believed iff φ is true in ALL minimal/best worlds.
        (Possible-worlds semantics for belief.)
        """
        min_worlds = self.minimal_worlds()
        if not min_worlds:
            return True   # vacuously true
        return all(interp_satisfies(w, phi, self.atoms) for w in min_worlds)

    def conditionally_believes(self, phi: Formula, given: Formula) -> bool:
        """
        Conditional belief: B(φ | given) — φ is true in all minimal given-worlds.
        """
        min_given = self.minimal_phi_worlds(given)
        if not min_given:
            return True  # vacuous
        return all(interp_satisfies(w, phi, self.atoms) for w in min_given)

    # ── Lexicographic Revision ────────────────────────────────

    def lex_revise(self, phi: Formula) -> "PlausibilityOrder":
        """
        Lexicographic revision by φ.

        For each rank level i, split into:
          φ-worlds at level i  (more plausible in new order)
          ¬φ-worlds at level i (less plausible in new order)

        New order: all φ-worlds in original rank order,
                   then all ¬φ-worlds in original rank order.

        This satisfies the Darwiche–Pearl postulates (C1–C4).
        """
        phi_ranks: List[Set[Interp]] = []
        neg_phi_ranks: List[Set[Interp]] = []

        for rank in self.ranks:
            phi_set = {w for w in rank if interp_satisfies(w, phi, self.atoms)}
            neg_set = {w for w in rank if not interp_satisfies(w, phi, self.atoms)}
            if phi_set:
                phi_ranks.append(phi_set)
            if neg_set:
                neg_phi_ranks.append(neg_set)

        new_ranks = phi_ranks + neg_phi_ranks
        # Remove empty ranks
        new_ranks = [r for r in new_ranks if r]
        return PlausibilityOrder(self.atoms, new_ranks)

    # ── Minimal (Natural) Revision ────────────────────────────

    def minimal_revise(self, phi: Formula) -> "PlausibilityOrder":
        """
        Minimal revision (natural revision) by φ.

        Only the most plausible φ-worlds are promoted to rank 0.
        Everything else stays in original order below them.

        This is less drastic than lexicographic revision.
        """
        # Find the lowest rank containing any φ-world
        best_phi_rank_idx = None
        best_phi_worlds: Set[Interp] = set()
        for i, rank in enumerate(self.ranks):
            phi_set = {w for w in rank if interp_satisfies(w, phi, self.atoms)}
            if phi_set:
                best_phi_rank_idx = i
                best_phi_worlds = phi_set
                break

        if best_phi_rank_idx is None:
            # φ has no models — revision not possible (should not happen with consistent φ)
            return PlausibilityOrder(self.atoms, [r.copy() for r in self.ranks])

        # Build new ranks:
        #  1. The best φ-worlds (extracted from their original rank)
        #  2. Everything else in original order

        new_ranks: List[Set[Interp]] = [best_phi_worlds]

        for i, rank in enumerate(self.ranks):
            if i == best_phi_rank_idx:
                remainder = rank - best_phi_worlds
                if remainder:
                    new_ranks.append(remainder)
            else:
                new_ranks.append(set(rank))

        new_ranks = [r for r in new_ranks if r]
        return PlausibilityOrder(self.atoms, new_ranks)

    # ── Display ───────────────────────────────────────────────

    def display(self) -> str:
        atom_list = sorted(self.atoms)
        lines = []
        for i, rank in enumerate(self.ranks):
            worlds_str = ",  ".join(format_world(w, atom_list) for w in sorted(rank))
            marker = " ← most plausible (believed)" if i == 0 else ""
            lines.append(f"  Rank {i}: {worlds_str}{marker}")
        return "\n".join(lines)

    def display_beliefs(self) -> str:
        min_worlds = self.minimal_worlds()
        atom_list = sorted(self.atoms)
        lines = ["Minimal worlds (believed true in all):"]
        for w in sorted(min_worlds):
            lines.append(f"  {format_world(w, atom_list)}")
        return "\n".join(lines)

    def __repr__(self):
        return f"PlausibilityOrder(atoms={self.atoms}, ranks={self.ranks})"


# ─────────────────────────────────────────────────────────────
#  Factory: create default plausibility order from formulas
# ─────────────────────────────────────────────────────────────

def order_from_formulas(formulas_with_priorities: List[Tuple[Formula, int]]) -> PlausibilityOrder:
    """
    Build a plausibility order from a set of ranked formulas.

    Uses the epistemic entrenchment / ranking construction:
    For each world w, its rank = number of formulas it violates weighted by priority.
    Worlds violating high-priority formulas are ranked lower (less plausible).
    """
    if not formulas_with_priorities:
        return PlausibilityOrder(set())

    # Collect all atoms
    all_atoms: Set[str] = set()
    for f, _ in formulas_with_priorities:
        all_atoms |= f.atoms()

    all_worlds_list = []
    for interp_dict in all_interpretations(all_atoms):
        w = frozenset(a for a, v in interp_dict.items() if v)
        all_worlds_list.append(w)

    # Rank each world by the sum of priorities of violated formulas
    def world_rank(w: Interp) -> int:
        interp_dict = {a: (a in w) for a in all_atoms}
        # Worlds violating higher priority formulas are less plausible
        # Use negated sum so higher violation score = higher rank index
        score = 0
        for f, priority in formulas_with_priorities:
            if not f.evaluate(interp_dict):
                score += priority
        return score

    scores = {w: world_rank(w) for w in all_worlds_list}
    unique_scores = sorted(set(scores.values()))

    ranks: List[Set[Interp]] = []
    for score in unique_scores:
        rank_set = {w for w in all_worlds_list if scores[w] == score}
        ranks.append(rank_set)

    return PlausibilityOrder(all_atoms, ranks)
