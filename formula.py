# formula classes / AST nodes
from lark import Lark, Transformer, exceptions
from pathlib import Path

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

GRAMMAR = Path("GRAMMAR.lark").read_text()

class ParseError(Exception):
    pass


class FormulaTransformer(Transformer):
    def atom(self, items):
        return Atom(str(items[0]))

    def truth(self, items):
        return Truth()

    def falsity(self, items):
        return Falsity()

    def not_(self, items):
        return Not(items[0])

    def and_(self, items):
        return And(items[0], items[1])

    def or_(self, items):
        return Or(items[0], items[1])

    def implies(self, items):
        return Implies(items[0], items[1])

    def iff(self, items):
        return Iff(items[0], items[1])


_parser = Lark(GRAMMAR, parser="lalr", transformer=FormulaTransformer())


def parse(text):
    try:
        return _parser.parse(text)
    except exceptions.LarkError as e:
        raise ParseError(str(e)) from e
