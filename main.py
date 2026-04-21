# demo / CLI / test scneario
from formula import Atom, And, Not, Implies, Or, Iff, Formula
from belief_base import BeliefBase

p = Atom("p")
q = Atom("q")
x = Atom("x")
f = And(p, q)

valuation = {"p": True, "q": False}
print(f.evaluate(valuation))  # True
y = Implies(f,x)

print(y.evaluate(valuation))

S = BeliefBase()
S.add(p, priority=1)
S.add(q, priority=2)
S.show()
S.add(And(p, q), priority=3)
S.show()
S.contract(p)
S.show()
from formula import Atom, And, Not
