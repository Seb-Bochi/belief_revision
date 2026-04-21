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

p = Atom("p")
q = Atom("q")

f1 = And(p, Not(q))
print(f1.evaluate({"p": True, "q": False}))   # True
print(f1.atoms())                             # {'p', 'q'}

f2 = Implies(p, q)
print(f2.evaluate({"p": True, "q": False}))   # False

f3 = Iff(p, q)
print(f3.evaluate({"p": True, "q": True}))    # True
print(f3.evaluate({"p": True, "q": False}))   # False

p = Atom("p")
q = Atom("q")
r = Atom("r")

print(to_cnf(Implies(p, q)))              # should look like (!p | q)
print(to_cnf(Implies(p, And(q, r))))      # should look like ((!p | q) & (!p | r))
print(to_cnf(Not(Or(p, q))))              # should look like (!p & !q)
