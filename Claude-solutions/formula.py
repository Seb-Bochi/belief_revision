"""
formula.py — Propositional logic formula AST

Supported syntax (string parsing):
  Atoms  : p, q, rain, etc.  (lowercase identifiers)
  Negation   : ~p  or  -p
  Conjunction: p & q
  Disjunction: p | q
  Implication: p -> q
  Biconditional: p <-> q

Precedence (low → high): <->, ->, |, &, ~
"""

from __future__ import annotations
from typing import Set, Dict, Optional, FrozenSet
import re
import itertools


# ─────────────────────────────────────────────
#  AST node types
# ─────────────────────────────────────────────

class Formula:
    """Abstract base for all formula nodes."""

    def atoms(self) -> Set[str]:
        raise NotImplementedError

    def evaluate(self, interp: Dict[str, bool]) -> bool:
        raise NotImplementedError

    def nnf(self) -> "Formula":
        """Return equivalent formula in Negation Normal Form."""
        raise NotImplementedError

    def cnf_clauses(self) -> "list[FrozenSet]":
        """Return list of clauses (frozensets of literals) in CNF."""
        return to_cnf_clauses(self.nnf())

    def __repr__(self):
        return str(self)

    # Operator overloads for convenient construction
    def __and__(self, other): return And(self, other)
    def __or__(self, other):  return Or(self, other)
    def __invert__(self):      return Neg(self)
    def __rshift__(self, other): return Implies(self, other)


class Atom(Formula):
    def __init__(self, name: str):
        self.name = name

    def atoms(self): return {self.name}
    def evaluate(self, interp): return interp[self.name]
    def nnf(self): return self

    def __str__(self): return self.name
    def __eq__(self, o): return isinstance(o, Atom) and self.name == o.name
    def __hash__(self): return hash(("Atom", self.name))


class Top(Formula):
    """Tautology (⊤)."""
    def atoms(self): return set()
    def evaluate(self, interp): return True
    def nnf(self): return self
    def __str__(self): return "⊤"
    def __eq__(self, o): return isinstance(o, Top)
    def __hash__(self): return hash("Top")


class Bot(Formula):
    """Contradiction (⊥)."""
    def atoms(self): return set()
    def evaluate(self, interp): return False
    def nnf(self): return self
    def __str__(self): return "⊥"
    def __eq__(self, o): return isinstance(o, Bot)
    def __hash__(self): return hash("Bot")


class Neg(Formula):
    def __init__(self, sub: Formula):
        self.sub = sub

    def atoms(self): return self.sub.atoms()

    def evaluate(self, interp): return not self.sub.evaluate(interp)

    def nnf(self):
        s = self.sub
        if isinstance(s, Neg):         return s.sub.nnf()
        if isinstance(s, And):         return Or(Neg(s.left).nnf(), Neg(s.right).nnf())
        if isinstance(s, Or):          return And(Neg(s.left).nnf(), Neg(s.right).nnf())
        if isinstance(s, Implies):     return And(s.left.nnf(), Neg(s.right).nnf())
        if isinstance(s, Biconditional):
            return Or(
                And(s.left.nnf(), Neg(s.right).nnf()),
                And(Neg(s.left).nnf(), s.right.nnf()),
            )
        if isinstance(s, Top):         return Bot()
        if isinstance(s, Bot):         return Top()
        return self  # Neg(Atom)

    def __str__(self): return f"~{self.sub}"
    def __eq__(self, o): return isinstance(o, Neg) and self.sub == o.sub
    def __hash__(self): return hash(("Neg", self.sub))


class And(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left, self.right = left, right

    def atoms(self): return self.left.atoms() | self.right.atoms()
    def evaluate(self, interp): return self.left.evaluate(interp) and self.right.evaluate(interp)

    def nnf(self): return And(self.left.nnf(), self.right.nnf())

    def __str__(self): return f"({self.left} & {self.right})"
    def __eq__(self, o): return isinstance(o, And) and self.left == o.left and self.right == o.right
    def __hash__(self): return hash(("And", self.left, self.right))


class Or(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left, self.right = left, right

    def atoms(self): return self.left.atoms() | self.right.atoms()
    def evaluate(self, interp): return self.left.evaluate(interp) or self.right.evaluate(interp)

    def nnf(self): return Or(self.left.nnf(), self.right.nnf())

    def __str__(self): return f"({self.left} | {self.right})"
    def __eq__(self, o): return isinstance(o, Or) and self.left == o.left and self.right == o.right
    def __hash__(self): return hash(("Or", self.left, self.right))


class Implies(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left, self.right = left, right

    def atoms(self): return self.left.atoms() | self.right.atoms()
    def evaluate(self, interp): return (not self.left.evaluate(interp)) or self.right.evaluate(interp)

    def nnf(self): return Or(Neg(self.left).nnf(), self.right.nnf())

    def __str__(self): return f"({self.left} -> {self.right})"
    def __eq__(self, o): return isinstance(o, Implies) and self.left == o.left and self.right == o.right
    def __hash__(self): return hash(("Implies", self.left, self.right))


class Biconditional(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left, self.right = left, right

    def atoms(self): return self.left.atoms() | self.right.atoms()
    def evaluate(self, interp): return self.left.evaluate(interp) == self.right.evaluate(interp)

    def nnf(self):
        return And(
            Or(Neg(self.left).nnf(), self.right.nnf()),
            Or(self.left.nnf(), Neg(self.right).nnf()),
        )

    def __str__(self): return f"({self.left} <-> {self.right})"
    def __eq__(self, o): return isinstance(o, Biconditional) and self.left == o.left and self.right == o.right
    def __hash__(self): return hash(("Biconditional", self.left, self.right))


# ─────────────────────────────────────────────
#  CNF conversion  (recursive distribution)
# ─────────────────────────────────────────────


def _nnf_to_cnf(f: Formula) -> list:
    """
    Convert an NNF formula to CNF clauses using the distributive law.
    Returns a list of frozensets (clauses).
    """
    if isinstance(f, Atom):
        return [frozenset({f.name})]
    if isinstance(f, Neg):
        assert isinstance(f.sub, Atom), f"Non-NNF negation: {f}"
        return [frozenset({f"~{f.sub.name}"})]
    if isinstance(f, Top):
        return []   # tautological — no constraints
    if isinstance(f, Bot):
        return [frozenset()]  # empty clause = contradiction
    if isinstance(f, And):
        return _nnf_to_cnf(f.left) + _nnf_to_cnf(f.right)
    if isinstance(f, Or):
        # Distribute: (C1 ∧ C2 ∧ …) ∨ (D1 ∧ D2 ∧ …)
        # = cross-product of clause sets, each pair joined by OR (set union)
        left_clauses  = _nnf_to_cnf(f.left)
        right_clauses = _nnf_to_cnf(f.right)
        if not left_clauses:   return right_clauses
        if not right_clauses:  return left_clauses
        result = []
        for lc in left_clauses:
            for rc in right_clauses:
                merged = lc | rc
                # Skip tautological clauses (contain p and ~p)
                taut = any(
                    (lit.startswith("~") and lit[1:] in merged) or
                    (not lit.startswith("~") and f"~{lit}" in merged)
                    for lit in merged
                )
                if not taut:
                    result.append(merged)
        return result
    raise ValueError(f"Unexpected formula type in NNF: {type(f).__name__}: {f}")


def formula_to_cnf_clauses(formula: Formula) -> list:
    """Public entry: convert any formula to CNF clause list."""
    nnf = formula.nnf()
    return _nnf_to_cnf(nnf)


# ─────────────────────────────────────────────
#  Parser
# ─────────────────────────────────────────────

class ParseError(Exception):
    pass


class _Tokenizer:
    TOKENS = re.compile(
        r"\s*(?:"
        r"(<->)"
        r"|(->)"
        r"|([|&~()])"
        r"|([A-Za-z_][A-Za-z0-9_]*)"
        r"|(⊤|⊥)"
        r")\s*"
    )

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.tokens: list = []
        self._tokenize()
        self.idx = 0

    def _tokenize(self):
        pos = 0
        while pos < len(self.text):
            m = self.TOKENS.match(self.text, pos)
            if not m:
                raise ParseError(f"Unexpected character at position {pos}: '{self.text[pos]}'")
            pos = m.end()
            tok = m.group(1) or m.group(2) or m.group(3) or m.group(4) or m.group(5)
            if tok:
                self.tokens.append(tok)

    def peek(self) -> Optional[str]:
        return self.tokens[self.idx] if self.idx < len(self.tokens) else None

    def consume(self) -> str:
        tok = self.tokens[self.idx]
        self.idx += 1
        return tok

    def expect(self, tok: str):
        actual = self.consume()
        if actual != tok:
            raise ParseError(f"Expected '{tok}', got '{actual}'")


def parse(text: str) -> Formula:
    """Parse a formula string into a Formula AST."""
    tok = _Tokenizer(text.strip())
    result = _parse_biconditional(tok)
    if tok.peek() is not None:
        raise ParseError(f"Unexpected token: {tok.peek()}")
    return result


def _parse_biconditional(tok: _Tokenizer) -> Formula:
    left = _parse_implication(tok)
    while tok.peek() == "<->":
        tok.consume()
        right = _parse_implication(tok)
        left = Biconditional(left, right)
    return left


def _parse_implication(tok: _Tokenizer) -> Formula:
    left = _parse_or(tok)
    while tok.peek() == "->":
        tok.consume()
        right = _parse_or(tok)
        left = Implies(left, right)
    return left


def _parse_or(tok: _Tokenizer) -> Formula:
    left = _parse_and(tok)
    while tok.peek() == "|":
        tok.consume()
        right = _parse_and(tok)
        left = Or(left, right)
    return left


def _parse_and(tok: _Tokenizer) -> Formula:
    left = _parse_neg(tok)
    while tok.peek() == "&":
        tok.consume()
        right = _parse_neg(tok)
        left = And(left, right)
    return left


def _parse_neg(tok: _Tokenizer) -> Formula:
    if tok.peek() == "~":
        tok.consume()
        sub = _parse_neg(tok)
        return Neg(sub)
    return _parse_atom(tok)


def _parse_atom(tok: _Tokenizer) -> Formula:
    t = tok.peek()
    if t is None:
        raise ParseError("Unexpected end of input")
    if t == "(":
        tok.consume()
        f = _parse_biconditional(tok)
        tok.expect(")")
        return f
    if t == "⊤":
        tok.consume()
        return Top()
    if t == "⊥":
        tok.consume()
        return Bot()
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", t):
        tok.consume()
        return Atom(t)
    raise ParseError(f"Unexpected token: '{t}'")


# ─────────────────────────────────────────────
#  Interpretation utilities
# ─────────────────────────────────────────────

def all_interpretations(atoms: Set[str]) -> list:
    """Return all 2^n interpretations over the given atom set."""
    atoms = sorted(atoms)
    result = []
    for bits in itertools.product([False, True], repeat=len(atoms)):
        result.append(dict(zip(atoms, bits)))
    return result


def models(formula: Formula, extra_atoms: Optional[Set[str]] = None) -> list:
    """Return all interpretations satisfying formula."""
    atom_set = formula.atoms()
    if extra_atoms:
        atom_set |= extra_atoms
    return [i for i in all_interpretations(atom_set) if formula.evaluate(i)]


def is_tautology(formula: Formula) -> bool:
    atom_set = formula.atoms()
    if not atom_set:
        return formula.evaluate({})
    return all(formula.evaluate(i) for i in all_interpretations(atom_set))


def is_contradiction(formula: Formula) -> bool:
    atom_set = formula.atoms()
    if not atom_set:
        return not formula.evaluate({})
    return not any(formula.evaluate(i) for i in all_interpretations(atom_set))


def formulas_equivalent(f1: Formula, f2: Formula) -> bool:
    atoms = f1.atoms() | f2.atoms()
    return all(f1.evaluate(i) == f2.evaluate(i) for i in all_interpretations(atoms))
