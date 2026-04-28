from itertools import product

from belief_base import BeliefBase
from formula import And, Atom, Formula, Iff, Implies, Not, Or, Truth


def belief_formula(bb: BeliefBase) -> Formula:
    """Collapse a belief base into a single conjunction for model checks."""
    if not bb.entries:
        return Truth()

    formula = bb.entries[0].formula
    for entry in bb.entries[1:]:
        formula = And(formula, entry.formula)
    return formula


def equivalent_formulas(left: Formula, right: Formula) -> bool:
    """Check semantic equivalence by brute force over the shared atoms."""
    atoms = sorted(left.atoms().union(right.atoms()))

    for values in product([False, True], repeat=len(atoms)):
        valuation = dict(zip(atoms, values))
        if left.evaluate(valuation) != right.evaluate(valuation):
            return False

    return True


def equivalent_bases(left: BeliefBase, right: BeliefBase) -> bool:
    return equivalent_formulas(belief_formula(left), belief_formula(right))


def is_subset_by_entry(left: BeliefBase, right: BeliefBase) -> bool:
    left_entries = {(repr(entry.formula), entry.priority) for entry in left.entries}
    right_entries = {(repr(entry.formula), entry.priority) for entry in right.entries}
    return left_entries.issubset(right_entries)


def clone_base(bb: BeliefBase) -> BeliefBase:
    return BeliefBase(entries=bb.entries.copy())


def revise_copy(bb: BeliefBase, formula: Formula, priority: int = 5) -> BeliefBase:
    revised = clone_base(bb)
    revised.revise(formula, priority)
    return revised


def contract_copy(bb: BeliefBase, formula: Formula) -> BeliefBase:
    contracted = clone_base(bb)
    contracted.contract(formula)
    return contracted


def print_result(name: str, passed: bool, detail: str) -> None:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {detail}")


def test_revision_postulates() -> bool:
    print("Revision AGM postulates")

    p = Atom("p")
    q = Atom("q")
    r = Atom("r")

    base = BeliefBase()
    base.add(Implies(p, q), 8)
    base.add(p, 6)

    phi = q
    psi = Or(q, And(q, r))

    revised = revise_copy(base, phi, priority=7)
    revised_equiv = revise_copy(base, psi, priority=7)
    expanded = clone_base(base)
    expanded.add(phi, 7)

    results = []

    success = revised.entails(phi)
    results.append(("Success", success, f"K * {phi} entails {phi}: {success}"))

    inclusion = is_subset_by_entry(revised, expanded)
    results.append(("Inclusion", inclusion, "Every stored belief in K*phi also appears in K+phi"))

    vacuity_pre = not base.entails(Not(phi))
    vacuity = equivalent_bases(revised, expanded) if vacuity_pre else False
    results.append(("Vacuity", vacuity, f"~phi not entailed by K: {vacuity_pre}; K*phi equivalent to K+phi: {vacuity}"))

    consistency = revised.is_consistent()
    results.append(("Consistency", consistency, f"K * {phi} is consistent: {consistency}"))

    extensionality_pre = equivalent_formulas(phi, psi)
    extensionality = equivalent_bases(revised, revised_equiv)
    results.append(("Extensionality", extensionality_pre and extensionality, f"phi <-> psi tautological: {extensionality_pre}; K*phi equivalent to K*psi: {extensionality}"))

    for name, passed, detail in results:
        print_result(name, passed, detail)

    return all(passed for _, passed, _ in results)


def test_contraction_postulates() -> bool:
    print("\nContraction AGM postulates")

    p = Atom("p")
    q = Atom("q")
    r = Atom("r")

    base = BeliefBase()
    base.add(Implies(p, q), 8)
    base.add(p, 6)
    base.add(r, 4)

    phi = q
    psi = Or(q, And(q, r))

    contracted = contract_copy(base, phi)
    contracted_equiv = contract_copy(base, psi)

    vacuous_base = BeliefBase()
    vacuous_base.add(p, 5)
    vacuous_base.add(r, 4)
    vacuous_contracted = contract_copy(vacuous_base, q)

    results = []

    success = not contracted.entails(phi)
    results.append(("Success", success, f"K - {phi} no longer entails {phi}: {success}"))

    inclusion = is_subset_by_entry(contracted, base)
    results.append(("Inclusion", inclusion, "Every stored belief in K-phi comes from K"))

    vacuity_pre = not vacuous_base.entails(q)
    vacuity = equivalent_bases(vacuous_contracted, vacuous_base)
    results.append(("Vacuity", vacuity_pre and vacuity, f"phi not entailed by K: {vacuity_pre}; K-phi equivalent to K: {vacuity}"))

    consistency = contracted.is_consistent()
    results.append(("Consistency", consistency, f"K - {phi} is consistent: {consistency}"))

    extensionality_pre = equivalent_formulas(phi, psi)
    extensionality = equivalent_bases(contracted, contracted_equiv)
    results.append(("Extensionality", extensionality_pre and extensionality, f"phi <-> psi tautological: {extensionality_pre}; K-phi equivalent to K-psi: {extensionality}"))

    for name, passed, detail in results:
        print_result(name, passed, detail)

    return all(passed for _, passed, _ in results)


if __name__ == "__main__":
    revision_ok = test_revision_postulates()
    contraction_ok = test_contraction_postulates()

    overall = revision_ok and contraction_ok
    print(f"\nOverall AGM result: {'PASS' if overall else 'FAIL'}")
