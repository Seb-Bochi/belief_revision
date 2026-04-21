from formula import Atom, Not, And, Or, Implies, Iff
from cnf import to_cnf
from itertools import combinations

def literal_from_formula(f):
    if isinstance(f, Atom):
    # Convert Atom("p") to ("p", True)
        return (f.name, True)
    # Convert Not(Atom("p")) to ("p", False)
    if isinstance(f, Not) and isinstance(f.operand, Atom):
        return (f.operand.name, False)


def clause_from_formula(f):
    # Convert a disjunction into one clause
    if isinstance(f, Or):
        return clause_from_formula(f.left).union(clause_from_formula(f.right))
    
    return {literal_from_formula(f)}


def clauses_from_cnf(f):
    # Convert a CNF formula into a list of clauses
    if isinstance(f, And):
        return clauses_from_cnf(f.left) + clauses_from_cnf(f.right)
    
    return [clause_from_formula(f)]


def complementary(l1, l2):
    # True when literals are the same atom with opposite signs
    return l1[0] == l2[0] and l1[1] != l2[1]


def resolve(ci, cj):
    resolvents = set ()

    for li in ci:
        for lj in cj:
            if complementary(li, lj):
                new_clause = (ci - {li}) | (cj - {lj})
                resolvents.add(frozenset(new_clause))
    
    return resolvents


def resolution(clauses):
    # Main resolution loop
    clauses = set(clauses)

    while True:
        new = set()

        for ci, cj in combinations(clauses, 2):
            resolvents = resolve(ci,cj)

            if frozenset() in resolvents:
                return True
        
            new = new.union(resolvents)

        if new.issubset(clauses):
            return False
        
        clauses = clauses.union(new)


def is_consistent(formulas):
    # True if formulas do not derive contradiction
    clauses = []

    for f in formulas:
        cnf_formula = to_cnf(f)
        clauses.extend(clauses_from_cnf(cnf_formula))

    clause_set = {frozenset(clause) for clause in clauses}

    return not resolution(clause_set)

    


def entails(premises, conclusion):
    # premises |= conclusion iff premises + !conclusion is inconsistent
    formulas = premises + [Not(conclusion)]
    clauses = []

    for f in formulas:
        cnf_formula = to_cnf(f)
        clauses.extend(clauses_from_cnf(cnf_formula))

    clause_set = {frozenset(clause) for clause in clauses}

    return resolution(clause_set)
