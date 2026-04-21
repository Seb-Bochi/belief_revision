# formula classes / AST nodes

class Formula:
    pass


class Atom(Formula):
    def __init__(self, name):
        self.name = name

    def evalutate(self, validation):
        return validation[self.name]

    def __repr__(self):
        return self.name

class Truth(Formula):
    def __init__(self, name):
        self.name = name
    
    def evaluate(self):
        return True

    def __repr__(self):
        return "True"
    
class Falsity(Formula):
    def __init__(self, name):
        self.name = name

    def evaluate(self):
        return False

    def __repr__(self):
        return "False"

class Not(Formula):
    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, valuation):
        return not self.operand.evaluate(valuation)

    def __repr__(self):
        return f"!{self.operand}"


class And(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, valuation):
        return self.left.evaluate(valuation) and self.right.evaluate(valuation)

    def __repr__(self):
        return f"({self.left} & {self.right})"

class Or(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, valuation):
        return self.left.evaluate(valuation) or self.right.evaluate(valuation)

    def __repr__(self):
        return f"({self.left} | {self.right})"
    
class Implies(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, valuation):
        if (self.left.evaluate(valuation) == True and self.right.evaluate(valuation) == False):
            return False
        else:
            return True

    def __repr__(self):
        return f"({self.left} -> {self.right})"
    
class Iaoi(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, valuation):
        if (self.left.evaluate(valuation) == True and self.right.evaluate(valuation) == True or self.left.evaluate(valuation) == False and self.right.evaluate(valuation) == False):
            return True
        else:
            return False

    def __repr__(self):
        return f"({self.left} <-> {self.right})"


# parser / printer
p = Atom("p")
q = Atom("q")
f = And(p,q)
print(f)