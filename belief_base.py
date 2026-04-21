# belief storage 
# priority handling
""" 
│  FORMULA SYNTAX                                             │
│    Atoms:         p, q, rain, flies, etc.                   │
│    Negation:      !p                                        │
│    Conjunction:   p & q                                     │
│    Disjunction:   p | q                                     │
│    Implication:   p -> q                                    │
│    Biconditional: p <-> q                                   │
│    Grouping:      (p | q) & ~r                              |

│  BELIEF BASE COMMANDS                                       │
│    expand <formula> [prio]    Expand belief base │
│    contract <formula>         Contract belief base          │
│    revise <formula> [prio]    Revise belief base (Levi)     │
│    entails <formula>          Check if K |= formula         │
│    show                       Display current belief base   │
│    consistent                 Check consistency             │
│    clear                      Clear belief base  
"""
"""
1. design and implementation of belief base;
2. design and implementation of a method for checking logical entailment (e.g., resolutionbased), you should implement it yourself, without using any existing packages;
3. implementation of contraction of belief base (based on a priority order on formulas in the
belief base);
4. implementation of expansion of belief base.
The output should be the resulting/new belief base.

"""
from formula import Atom, And, Or, Not, Implies, Iff, Formula

p = Atom("p")
q = Atom("q")
class BeliefEntry:
    def __init__(self, formula: Formula, priority: int):
        self.formula = formula
        self.priority = priority

    def __repr__(self):
        return f"[{self.priority}] {self.formula}"
    
class BeliefBase:
    
    def __init__(self, entries: list[BeliefEntry] = None):
        self.entries = entries if entries is not None else []
    
    def add(self, formula: Formula, priority: int = 5):
        self.entries.append(BeliefEntry(formula, priority))

    def contract(self, formula: Formula):
        # remove all entries that entail the formula using the maximal consistent subset
        self.entries = self.maximal_consistent_subset(formula)
        
    
    def revise(self, formula: Formula, priority: int = 5):
        # contraction + expansion
        self.contract(formula)
        self.add(formula, priority)

    def entails(self, formula: Formula) -> bool:
        # check if any entry in the belief base entails the formula
        for entry in self.entries:
            if self.entails(entry.formula, formula):
                return True
        return False

    def is_consistent(self) -> bool:
        # check if the belief base is consistent (no contradictions)
        for i in range(len(self.entries)):
            for j in range(i + 1, len(self.entries)):
                if self.entails(self.entries[i].formula, Not(self.entries[j].formula)):
                    return False
        return True
    def show(self):
        for entry in self.entries:
            print(entry)
    
    def clear(self):
        self.entries = []
    
    def is_empty(self) -> bool:
        return len(self.entries) == 0
    
    def __repr__(self):
        return "\n".join(str(entry) for entry in self.entries)
    
    def copy(self):
        return BeliefBase(entries=self.entries.copy())
    
    def maximal_consistent_subset(self, formula: Formula) -> list[BeliefEntry]:
        # find the maximal consistent subset of the belief base that does not entail the formula
        consistent_subset = []
        for entry in self.entries:
            if not self.entails(entry.formula):
                consistent_subset.append(entry)
        return consistent_subset
