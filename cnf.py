from formula import Atom, Truth, Falsity, Not, And, Or, Implies, Iff

# implication elimination
def eliminate_implications(f):
    if isinstance(f, Atom):
        return f
    if isinstance(f, Truth):
        return f
    if isinstance(f, Falsity):
        return f
    if isinstance(f, Not):
        return Not(eliminate_implications(f.operand))
    if isinstance(f, And):
        return And(eliminate_implications(f.left), eliminate_implications(f.right))
    if isinstance(f, Or):
        return Or(eliminate_implications(f.left), eliminate_implications(f.right))
    if isinstance(f, Implies):
        return Or(Not(eliminate_implications(f.left)), eliminate_implications(f.right))
    if isinstance(f,Iff):
        return And(Or(Not(eliminate_implications(f.left)), eliminate_implications(f.right)), Or(Not(eliminate_implications(f.right)), eliminate_implications(f.left)))
# NNF
def to_nnf(f):
    if isinstance(f, (Atom, Truth, Falsity)):
        return f
    if isinstance(f, Not):
        inner = f.operand

        if isinstance(inner, Atom):
            return f
        if isinstance(inner, Truth):
            return Falsity()
        if isinstance(inner, Falsity):
            return Truth()
        if isinstance(inner, Not):
            return to_nnf(inner.operand)
        if isinstance(inner, And):
            return Or(to_nnf(Not(inner.left)), to_nnf(Not(inner.right)))
        if isinstance(inner, Or):
            return And(to_nnf(Not(inner.left)), to_nnf(Not(inner.right)))
    
    if isinstance(f, And):
        return And(to_nnf(f.left), to_nnf(f.right))
    if isinstance(f, Or):
        return Or(to_nnf(f.left), to_nnf(f.right))
# distribute or
def distribute_or(left, right):
    if isinstance(left, And):
        return And(
            distribute_or(left.left, right),
            distribute_or(left.right, right)
        )
    if isinstance(right, And):
        return And(
            distribute_or(left, right.left),
            distribute_or(left, right.right)
        )
    return Or(left, right)
#cnf conversion
def cnf_from_nnf(f):
    if isinstance(f, (Atom, Truth, Falsity)):
        return f
    if isinstance(f, Not):
        return f
    if isinstance(f, And):
        return And(cnf_from_nnf(f.left), cnf_from_nnf(f.right))
    if isinstance(f, Or):
        return distribute_or(cnf_from_nnf(f.left), cnf_from_nnf(f.right))

def to_cnf(f):
    f = eliminate_implications(f)
    f = to_nnf(f)
    f = cnf_from_nnf(f)
    return f