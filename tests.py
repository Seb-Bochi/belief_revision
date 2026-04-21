# unit tests 
from formula import Atom, Not, And, Or, Implies, Iff

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
