# contraction
# expansion
from belief_base import BeliefBase
from formula import Formula

def contract(belief_base: BeliefBase, formula: Formula) -> BeliefBase:
    """
    Contraction: K ÷ φ
    Remove beliefs that entail the formula using maximal consistent subset.
    Returns a new belief base without modifying the original.
    """
    result = belief_base.copy()
    result.contract(formula)
    return result

def expand(belief_base: BeliefBase, formula: Formula, priority: int = 5) -> BeliefBase:
    """
    Expansion: K + φ
    Add a formula to the belief base with given priority.
    Returns a new belief base without modifying the original.
    """
    result = belief_base.copy()
    result.add(formula, priority)
    return result

def revise(belief_base: BeliefBase, formula: Formula, priority: int = 5) -> BeliefBase:
    """
    Revision: K * φ
    Contract by ¬φ then expand by φ (Levi identity).
    Returns a new belief base without modifying the original.
    """
    result = belief_base.copy()
    result.revise(formula, priority)
    return result