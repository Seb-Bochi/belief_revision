# unit tests
#
# Formula commands used in this file:
# Atom("p")        = an atomic proposition, for example p
# Not(f)           = negation, meaning "not f"
# And(f, g)        = conjunction, meaning "f and g"
# Or(f, g)         = disjunction, meaning "f or g"
# Implies(f, g)    = implication, meaning "if f then g"
# Iff(f, g)        = biconditional, meaning "f if and only if g"
#
# Useful methods:
# evaluate({...})  = checks whether a formula is true under a given valuation
# atoms()          = returns the set of atomic propositions used in a formula

from formula import Atom, Not, And, Or, Implies, Iff
from cnf import to_cnf
from resolution import is_consistent, entails

# atoms
p = Atom("p")
q = Atom("q")
r = Atom("r")

# -----------------------
# Formula evaluation tests
# -----------------------
f1 = And(p, Not(q))
print("f1 =", f1)
print("f1 evaluate:", f1.evaluate({"p": True, "q": False}))   # True
print("f1 atoms:", f1.atoms())                                # {'p', 'q'}

f2 = Or(p, q)
print("f2 =", f2)
print("f2 evaluate:", f2.evaluate({"p": False, "q": True}))   # True

f3 = Implies(p, q)
print("f3 =", f3)
print("f3 evaluate:", f3.evaluate({"p": True, "q": False}))   # False

f4 = Iff(p, q)
print("f4 =", f4)
print("f4 evaluate:", f4.evaluate({"p": True, "q": True}))    # True
print("f4 evaluate:", f4.evaluate({"p": True, "q": False}))   # False

# -----------------------
# CNF tests
# -----------------------
print("\nCNF tests:")

cnf1 = to_cnf(Implies(p, q))
print("CNF of (p -> q):", cnf1)   # expected: (!p | q)

cnf2 = to_cnf(Implies(p, And(q, r)))
print("CNF of (p -> (q & r)):", cnf2)   # expected: ((!p | q) & (!p | r))

cnf3 = to_cnf(Not(Or(p, q)))
print("CNF of !(p | q):", cnf3)   # expected: (!p & !q)

# -----------------------
# Consistency tests
# -----------------------
print("\nConsistency tests:")

print("Is [p] consistent?", is_consistent([p]))                     # True
print("Is [p, !p] consistent?", is_consistent([p, Not(p)]))        # False
print("Is [p, p -> q, !q] consistent?", is_consistent([p, Implies(p, q), Not(q)]))  # False

# -----------------------
# Entailment tests
# -----------------------
print("\nEntailment tests:")

print("Do [p, p -> q] entail q?", entails([p, Implies(p, q)], q))   # True
print("Do [q] entail p?", entails([q], p))                          # False
print("Do [p & q] entail p?", entails([And(p, q)], p))              # True