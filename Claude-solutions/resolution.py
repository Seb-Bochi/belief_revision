"""
resolution.py — Resolution-based logical entailment

Implements the Davis–Putnam resolution procedure from scratch.
No external logic packages used.

Key function:
    entails(premises: list[Formula], conclusion: Formula) -> bool

Returns True iff premises |= conclusion, i.e., the set
{premise_1, ..., premise_n, ~conclusion} is unsatisfiable.
"""

from __future__ import annotations
from typing import FrozenSet, List, Set, Optional
from formula import Formula, Neg, Bot, Top, formula_to_cnf_clauses, is_contradiction


# A literal is a string: "p" for positive, "~p" for negative.
Literal = str
Clause = FrozenSet[Literal]


def negate_literal(lit: Literal) -> Literal:
    if lit.startswith("~"):
        return lit[1:]
    return f"~{lit}"


def is_tautological_clause(clause: Clause) -> bool:
    """A clause is a tautology if it contains both p and ~p."""
    for lit in clause:
        if negate_literal(lit) in clause:
            return True
    return False


def resolve(c1: Clause, c2: Clause) -> Optional[Clause]:
    """
    Try to resolve two clauses on exactly one complementary literal pair.
    Returns the resolvent, or None if no single complementary pair exists.
    If multiple pairs exist the clauses are not resolvable (would be a factor).
    """
    resolvent_lits = None
    pivot_count = 0
    for lit in c1:
        if negate_literal(lit) in c2:
            pivot_count += 1
            new_clause = (c1 - {lit}) | (c2 - {negate_literal(lit)})
            resolvent_lits = frozenset(new_clause)
    if pivot_count == 1:
        return resolvent_lits
    return None


def pl_resolution(clauses: List[Clause]) -> bool:
    """
    Apply PL-Resolution. Returns True iff the clause set is unsatisfiable
    (i.e., the empty clause [] can be derived).

    Uses the set-of-support strategy variant: iterative new-clause addition.
    """
    # Remove tautological clauses upfront
    clause_set: Set[Clause] = set()
    for c in clauses:
        if not is_tautological_clause(c):
            clause_set.add(c)

    # Empty clause immediately → unsat
    if frozenset() in clause_set:
        return True

    # Iterative resolution
    while True:
        new: Set[Clause] = set()
        clause_list = list(clause_set)
        n = len(clause_list)
        for i in range(n):
            for j in range(i + 1, n):
                resolvent = resolve(clause_list[i], clause_list[j])
                if resolvent is None:
                    continue
                if is_tautological_clause(resolvent):
                    continue
                if resolvent == frozenset():
                    return True   # Derived empty clause → unsatisfiable
                new.add(resolvent)
        new -= clause_set
        if not new:
            return False   # No new clauses → satisfiable
        clause_set |= new


def formula_to_clauses(formula: Formula) -> List[Clause]:
    """Convert a formula to its CNF clause list."""
    return formula_to_cnf_clauses(formula)


def entails(premises: List[Formula], conclusion: Formula) -> bool:
    """
    Check whether premises |= conclusion using resolution refutation.
    Builds the clause set of:  premises ∪ {¬conclusion}
    and checks unsatisfiability.
    """
    all_clauses: List[Clause] = []

    for p in premises:
        all_clauses.extend(formula_to_clauses(p))

    # Negate the conclusion
    neg_conclusion = Neg(conclusion)
    all_clauses.extend(formula_to_clauses(neg_conclusion))

    return pl_resolution(all_clauses)


def is_satisfiable(formula: Formula) -> bool:
    """Check if a formula is satisfiable (not all refuted)."""
    clauses = formula_to_clauses(formula)
    return not pl_resolution(clauses)


def is_consistent_set(formulas: List[Formula]) -> bool:
    """Check if a set of formulas is jointly satisfiable."""
    all_clauses: List[Clause] = []
    for f in formulas:
        all_clauses.extend(formula_to_clauses(f))
    return not pl_resolution(all_clauses)


def clause_set_entails(clauses: List[Clause], conclusion: Formula) -> bool:
    """Check entailment given pre-computed clauses + a conclusion formula."""
    extra = formula_to_clauses(Neg(conclusion))
    return pl_resolution(list(clauses) + extra)
