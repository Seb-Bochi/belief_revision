# demo / CLI / test scneario
from formula import Atom, And, Not

p = Atom("p")
q = Atom("q")
f = And(p, q)

valuation = {"p": True, "q": False}
print(f.evaluate(valuation))  # True