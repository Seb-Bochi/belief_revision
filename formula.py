# formula classes / AST nodes

class Formula:
    pass


class Atom(Formula):
    def __init__(self, name):
        self.name = name

    def evaluate(self, valuation):
        return valuation[self.name]
    
    def atoms(self):
        return {self.name}

    def __repr__(self):
        return self.name

class Truth(Formula):
    def evaluate(self, valuation):
        return True
    
    def atoms(self):
        return set()

    def __repr__(self):
        return "True"
    
class Falsity(Formula):
    def evaluate(self, valuation):
        return False
    
    def atoms(self):
        return set()

    def __repr__(self):
        return "False"

class Not(Formula):
    def __init__(self, operand):
        self.operand = operand

    def evaluate(self, valuation):
        return not self.operand.evaluate(valuation)
    
    def atoms(self):
        return self.operand.atoms()

    def __repr__(self):
        return f"!{self.operand}"


class And(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, valuation):
        return self.left.evaluate(valuation) and self.right.evaluate(valuation)

    def atoms(self):
        return self.left.atoms().union(self.right.atoms())

    def __repr__(self):
        return f"({self.left} & {self.right})"

class Or(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, valuation):
        return self.left.evaluate(valuation) or self.right.evaluate(valuation)
    
    def atoms(self):
        return self.left.atoms().union(self.right.atoms())

    def __repr__(self):
        return f"({self.left} | {self.right})"
    
class Implies(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, valuation):
        return (not self.left.evaluate(valuation)) or self.right.evaluate(valuation)
    
    def atoms(self):
        return self.left.atoms().union(self.right.atoms())

    def __repr__(self):
        return f"({self.left} -> {self.right})"
    
class Iff(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, valuation):
        return self.left.evaluate(valuation) == self.right.evaluate(valuation)
    
    def atoms(self):
        return self.left.atoms().union(self.right.atoms())

    def __repr__(self):
        return f"({self.left} <-> {self.right})"
