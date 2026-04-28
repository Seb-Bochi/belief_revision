from lark import Lark, Transformer, v_args
from formula import Atom, Truth, Falsity, Not, And, Or, Implies, Iff

@v_args(inline=True)
class LogicTransformer(Transformer):
    def atom(self, name):
        return Atom(str(name))

    def truth(self):
        return Truth()

    def falsity(self):
        return Falsity()

    def not_(self, operand):
        return Not(operand)

    def and_(self, left, right):
        return And(left, right)

    def or_(self, left, right):
        return Or(left, right)

    def implies(self, left, right):
        return Implies(left, right)

    def iff(self, left, right):
        return Iff(left, right)

    def priority(self, value):
        return int(value)

    def add(self, formula, priority=5):
        return ("add", formula, priority)

    def expand(self, formula, priority=5):
        return ("expand", formula, priority)

    def revise(self, formula, priority=5):
        return ("revise", formula, priority)

    def contract(self, formula):
        return ("contract", formula)

    def entails(self, formula):
        return ("entails", formula)

    def show(self):
        return ("show",)

    def consistent(self):
        return ("consistent",)

    def clear(self):
        return ("clear",)

    def help(self):
        return ("help",)

    def demo(self):
        return ("demo",)

    def quit(self):
        return ("quit",)


parser = Lark(
    GRAMMAR,
    parser="lalr",
    transformer=LogicTransformer(),
)


def parse(text: str):
    return parser.parse(text)


def parse_formula(text: str):
    result = parser.parse(text)

    if isinstance(result, tuple):
        raise ValueError(f"Expected formula, got command: {text}")

    return result


def parse_command(text: str):
    result = parser.parse(text)

    if not isinstance(result, tuple):
        raise ValueError(f"Expected command, got formula: {text}")

    return result