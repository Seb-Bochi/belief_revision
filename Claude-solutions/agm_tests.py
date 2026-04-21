"""
agm_tests.py — Test AGM revision postulates

Tests for both:
  (A) Belief-base revision (partial meet contraction)
  (B) Plausibility-order revision

AGM Revision Postulates (for K * φ):
  (R*1) Closure       — K*φ is a belief set
  (R*2) Success       — φ ∈ K*φ
  (R*3) Inclusion     — K*φ ⊆ K+φ
  (R*4) Vacuity       — if ~φ ∉ K, then K+φ ⊆ K*φ
  (R*5) Consistency   — K*φ is consistent (if φ is consistent)
  (R*6) Extensionality— if φ ≡ ψ, then K*φ = K*ψ

AGM Contraction Postulates (for K ÷ φ):
  (K-1) Closure       — K÷φ is a belief set
  (K-2) Inclusion     — K÷φ ⊆ K
  (K-3) Vacuity       — if φ ∉ K, then K÷φ = K
  (K-4) Success       — if ⊬ φ, then φ ∉ K÷φ
  (K-5) Recovery      — K ⊆ (K÷φ)+φ
  (K-6) Extensionality— if φ ≡ ψ, then K÷φ = K÷ψ
"""

from __future__ import annotations
from typing import List, Tuple
from formula import Formula, parse, formulas_equivalent, is_contradiction
from belief_base import BeliefBase, BeliefEntry
from plausibility import PlausibilityOrder, order_from_formulas, interp_satisfies
from resolution import entails, is_consistent_set


PASS = "✅ PASS"
FAIL = "❌ FAIL"
SKIP = "⚠️  SKIP"


def _check(condition: bool, name: str, detail: str = "") -> Tuple[bool, str]:
    status = PASS if condition else FAIL
    msg = f"  {status}  {name}"
    if detail:
        msg += f"\n         {detail}"
    return condition, msg


def run_contraction_postulates(bb: BeliefBase, phi: Formula) -> List[Tuple[bool, str]]:
    """Test AGM contraction postulates for K ÷ φ."""
    results = []
    contracted = bb.contract(phi)

    # K-2 Inclusion: K÷φ ⊆ K (every formula in contracted is in original)
    original_set = {str(f) for f in bb.formulas()}
    contracted_set = {str(f) for f in contracted.formulas()}
    inclusion_ok = contracted_set.issubset(original_set)
    results.append(_check(inclusion_ok, "Inclusion (K÷φ ⊆ K)",
        f"contracted={contracted_set}, original={original_set}"))

    # K-3 Vacuity: if φ ∉ Cn(K), then K÷φ = K
    k_entails_phi = bb.entails(phi)
    if not k_entails_phi:
        vacuity_ok = contracted_set == original_set
        results.append(_check(vacuity_ok, "Vacuity (φ∉Cn(K) ⟹ K÷φ=K)",
            f"K entails φ={k_entails_phi}"))
    else:
        results.append((True, f"  {SKIP}  Vacuity (K entails φ, so vacuity doesn't apply)"))

    # K-4 Success: if ⊬ φ (φ not a tautology), then φ ∉ Cn(K÷φ)
    from belief_base import _is_tautology_formula
    phi_is_taut = _is_tautology_formula(phi)
    if not phi_is_taut:
        success_ok = not contracted.entails(phi)
        results.append(_check(success_ok, "Success (⊬φ ⟹ φ∉Cn(K÷φ))",
            f"K÷φ entails φ: {contracted.entails(phi)}"))
    else:
        results.append((True, f"  {SKIP}  Success (φ is a tautology)"))

    # K-6 Extensionality: if φ ≡ ψ then K÷φ = K÷ψ
    # Test with ψ = ~(~φ), which is logically equivalent to φ
    from formula import Neg
    psi = Neg(Neg(phi))
    contracted2 = bb.contract(psi)
    c1_forms = contracted.formulas()
    c2_forms = contracted2.formulas()
    # Use semantic equivalence: K÷φ and K÷ψ should entail the same things
    # Check that each base entails all formulas of the other
    ext_ok = (
        all(entails(c2_forms, f) for f in c1_forms) and
        all(entails(c1_forms, f) for f in c2_forms)
    )
    results.append(_check(ext_ok, "Extensionality (φ≡ψ ⟹ K÷φ≡K÷ψ)",
        f"K÷φ size={len(c1_forms)}, K÷~~φ size={len(c2_forms)}, semantically equiv={ext_ok}"))

    # K-5 Recovery: K ⊆ Cn((K÷φ) + φ)
    recovered = contracted.expand(phi, priority=10)
    recovery_ok = all(recovered.entails(f) for f in bb.formulas())
    results.append(_check(recovery_ok, "Recovery (K ⊆ Cn((K÷φ)+φ))"))

    return results


def run_revision_postulates(bb: BeliefBase, phi: Formula, priority: int = 5) -> List[Tuple[bool, str]]:
    """Test AGM revision postulates for K * φ."""
    results = []
    revised = bb.revise(phi, priority)

    # R*2 Success: φ ∈ K*φ
    success_ok = revised.entails(phi)
    results.append(_check(success_ok, "Success (φ ∈ K*φ)",
        f"K*φ entails φ: {success_ok}"))

    # R*3 Inclusion: K*φ ⊆ K+φ
    expanded = bb.expand(phi, priority)
    revised_set = {str(f) for f in revised.formulas()}
    expanded_set = {str(f) for f in expanded.formulas()}
    # Inclusion: everything in K*φ should be entailed by K+φ
    inclusion_ok = all(expanded.entails(f) for f in revised.formulas())
    results.append(_check(inclusion_ok, "Inclusion (K*φ ⊆ K+φ)",
        f"revised={revised_set}"))

    # R*4 Vacuity: if ~φ ∉ K, then K+φ ⊆ K*φ
    from formula import Neg
    neg_phi = Neg(phi)
    k_entails_neg_phi = bb.entails(neg_phi)
    if not k_entails_neg_phi:
        vacuity_ok = all(revised.entails(f) for f in expanded.formulas())
        results.append(_check(vacuity_ok, "Vacuity (~φ∉K ⟹ K+φ⊆K*φ)"))
    else:
        results.append((True, f"  {SKIP}  Vacuity (~φ ∈ K, revision is non-trivial)"))

    # R*5 Consistency: K*φ is consistent (if φ is consistent)
    from resolution import is_satisfiable
    phi_consistent = is_satisfiable(phi)
    if phi_consistent:
        cons_ok = revised.is_consistent()
        results.append(_check(cons_ok, "Consistency (K*φ consistent if φ consistent)",
            f"K*φ consistent: {cons_ok}"))
    else:
        results.append((True, f"  {SKIP}  Consistency (φ itself is inconsistent)"))

    # R*6 Extensionality: if φ ≡ ψ then K*φ = K*ψ
    from formula import Neg
    psi = Neg(Neg(phi))
    revised2 = bb.revise(psi, priority)
    r1_forms = revised.formulas()
    r2_forms = revised2.formulas()
    # Semantic equivalence: each base entails all formulas of the other
    ext_ok = (
        all(entails(r2_forms, f) for f in r1_forms) and
        all(entails(r1_forms, f) for f in r2_forms)
    )
    results.append(_check(ext_ok, "Extensionality (φ≡ψ ⟹ K*φ≡K*ψ)",
        f"K*φ size={len(r1_forms)}, K*~~φ size={len(r2_forms)}, semantically equiv={ext_ok}"))

    return results


# ──────────────────────────────────────────────────────────
#  Plausibility-order postulate tests (Darwiche-Pearl)
# ──────────────────────────────────────────────────────────

def run_plausibility_postulates(order: PlausibilityOrder, phi: Formula, mu: Formula) -> List[Tuple[bool, str]]:
    """
    Test Darwiche-Pearl postulates for iterated revision.
    (C1) If μ |= φ, then (K*φ)*μ = K*μ
    (C2) If μ |= ~φ, then (K*φ)*μ = K*μ
    (C3) If K*μ |= φ, then (K*φ)*μ |= φ
    (C4) If K*μ ⊭ ~φ, then (K*φ)*μ ⊭ ~φ
    """
    results = []
    from formula import Neg

    kphi = order.lex_revise(phi)
    kmu = order.lex_revise(mu)
    kphi_mu = kphi.lex_revise(mu)

    # Entailment in plausibility order = all minimal worlds satisfy formula
    def po_entails(po: PlausibilityOrder, f: Formula) -> bool:
        return po.believes(f)

    # (C1) μ |= φ → (K*φ)*μ = K*μ
    # Check if mu semantically entails phi
    from resolution import entails as res_entails
    mu_entails_phi = res_entails([mu], phi)
    if mu_entails_phi:
        # Ranks should match
        c1_ok = _orders_equivalent(kphi_mu, kmu)
        results.append(_check(c1_ok, "(C1) μ⊨φ ⟹ (K*φ)*μ ≡ K*μ"))
    else:
        results.append((True, f"  {SKIP}  (C1): μ does not entail φ"))

    # (C2) μ |= ~φ → (K*φ)*μ = K*μ
    neg_phi = Neg(phi)
    mu_entails_negphi = res_entails([mu], neg_phi)
    if mu_entails_negphi:
        c2_ok = _orders_equivalent(kphi_mu, kmu)
        results.append(_check(c2_ok, "(C2) μ⊨~φ ⟹ (K*φ)*μ ≡ K*μ"))
    else:
        results.append((True, f"  {SKIP}  (C2): μ does not entail ~φ"))

    # (C3) K*μ |= φ → (K*φ)*μ |= φ
    kmu_believes_phi = po_entails(kmu, phi)
    if kmu_believes_phi:
        c3_ok = po_entails(kphi_mu, phi)
        results.append(_check(c3_ok, "(C3) K*μ⊨φ ⟹ (K*φ)*μ⊨φ"))
    else:
        results.append((True, f"  {SKIP}  (C3): K*μ does not believe φ"))

    # (C4) K*μ ⊭ ~φ → (K*φ)*μ ⊭ ~φ
    kmu_not_negphi = not po_entails(kmu, neg_phi)
    if kmu_not_negphi:
        c4_ok = not po_entails(kphi_mu, neg_phi)
        results.append(_check(c4_ok, "(C4) K*μ⊭~φ ⟹ (K*φ)*μ⊭~φ"))
    else:
        results.append((True, f"  {SKIP}  (C4): K*μ believes ~φ"))

    return results


def _orders_equivalent(o1: PlausibilityOrder, o2: PlausibilityOrder) -> bool:
    """Two plausibility orders are equivalent if their rank structure matches."""
    if len(o1.ranks) != len(o2.ranks):
        return False
    for r1, r2 in zip(o1.ranks, o2.ranks):
        if r1 != r2:
            return False
    return True


def print_results(results: List[Tuple[bool, str]], title: str):
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")
    all_pass = True
    for ok, msg in results:
        print(msg)
        if not ok:
            all_pass = False
    print(f"{'─'*60}")
    print(f"  Overall: {'✅ All postulates satisfied' if all_pass else '❌ Some postulates FAILED'}")
    print(f"{'═'*60}")
    return all_pass
