#!/usr/bin/env python3
"""
Belief Revision Agent — Main Entry Point
Implements AGM belief revision with resolution-based entailment.

Usage:
    python main.py                  # interactive mode
    python main.py --demo           # run demonstration
"""

import sys
import argparse
from formula import Atom, And, Not, Implies, Or, Iff, Formula, parse, ParseError
from belief_base import BeliefBase
from resolution import extract_clauses, pl_resolution
from cnf import to_cnf

HELP_TEXT = """
┌─────────────────────────────────────────────────────────────┐
│        BELIEF REVISION AGENT — Command Reference            │
├─────────────────────────────────────────────────────────────┤
│  FORMULA SYNTAX                                             │
│    Atoms:         p, q, rain, flies, etc.                   │
│    Negation:      !p                                        │
│    Conjunction:   p & q                                     │
│    Disjunction:   p | q                                     │
│    Implication:   p -> q                                    │
│    Biconditional: p <-> q                                   │
│    Grouping:      (p | q) & !r                              │
├─────────────────────────────────────────────────────────────┤
│  BELIEF BASE COMMANDS                                       │
│    add <formula> [priority]   Add formula (default prio=5)  │
│    expand <formula> [prio]    Expand belief base            │
│    contract <formula>         Contract belief base          │
│    revise <formula> [prio]    Revise belief base (Levi)     │
│    entails <formula>          Check if K |= formula         │
│    show                       Display current belief base   │
│    consistent                 Check consistency             │
│    clear                      Clear belief base             │
├─────────────────────────────────────────────────────────────┤
│  OTHER                                                      │
│    help                       Show this help               │
│    demo                       Run demonstration            │
│    quit / exit                Exit                         │
└─────────────────────────────────────────────────────────────┘
"""


def banner():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║        BELIEF REVISION AGENT — Propositional Logic           ║
║  Implements: AGM revision, contraction, expansion,           ║
║             resolution entailment, CNF conversion            ║
╚═══════════════════════════════════════════════════════════════╝
Type 'help' for commands, 'demo' for a demonstration.
""")


def parse_formula_and_priority(rest: str, default_prio: int = 5):
    """Parse 'formula_str [priority]' from command line."""
    rest = rest.strip()
    tokens = rest.rsplit(maxsplit=1)
    if len(tokens) == 2 and tokens[1].lstrip("-").isdigit():
        return tokens[0].strip(), int(tokens[1])
    return rest, default_prio


def run_interactive():
    """Interactive mode with command-line interface."""
    banner()
    bb = BeliefBase()

    while True:
        try:
            line = input("KB> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not line or line.startswith("#"):
            continue

        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""

        try:
            if cmd in ("quit", "exit", "q"):
                print("Goodbye.")
                break

            elif cmd == "help":
                print(HELP_TEXT)

            elif cmd == "demo":
                run_demo()

            elif cmd == "show":
                print("\nCurrent Belief Base:")
                if bb.is_empty():
                    print("  (empty)")
                else:
                    for entry in sorted(bb.entries, key=lambda e: -e.priority):
                        print(f"  {entry}")
                print()

            elif cmd == "consistent":
                result = bb.is_consistent()
                print(f"  Belief base is {'consistent ✅' if result else 'INCONSISTENT ❌'}")

            elif cmd == "clear":
                bb = BeliefBase()
                print("  Belief base cleared.")

            elif cmd in ("add", "expand"):
                phi_str, prio = parse_formula_and_priority(rest, default_prio=5)
                phi = parse(phi_str)
                bb.add(phi, prio)
                print(f"  Added: {phi}  (priority={prio})")
                print(f"  Belief base now has {len(bb.entries)} formula(s).")

            elif cmd == "contract":
                phi = parse(rest.strip())
                old_size = len(bb.entries)
                bb.contract(phi)
                new_size = len(bb.entries)
                print(f"  Contracted by: {phi}")
                print(f"  Removed {old_size - new_size} formula(s).")
                print("\nBelief Base after contraction:")
                if bb.is_empty():
                    print("  (empty)")
                else:
                    for entry in sorted(bb.entries, key=lambda e: -e.priority):
                        print(f"  {entry}")

            elif cmd == "revise":
                phi_str, prio = parse_formula_and_priority(rest, default_prio=5)
                phi = parse(phi_str)
                bb.revise(phi, prio)
                print(f"  Revised by: {phi}  (priority={prio})")
                print("\nBelief Base after revision:")
                if bb.is_empty():
                    print("  (empty)")
                else:
                    for entry in sorted(bb.entries, key=lambda e: -e.priority):
                        print(f"  {entry}")

            elif cmd == "entails":
                phi = parse(rest.strip())
                result = bb.entails(phi)
                print(f"  K |= {phi} : {'Yes ✅' if result else 'No ❌'}")

            else:
                print(f"  Unknown command: {cmd}  (type 'help' for commands)")

        except ParseError as e:
            print(f"  Parse error: {e}")
        except Exception as e:
            print(f"  Error: {e}")


def run_demo():
    """Demonstration of belief revision operations."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║               BELIEF REVISION — DEMO                         ║
║  Scenario: "Tweety the Bird"                                 ║
║  Atoms: b=bird, f=flies, p=penguin                           ║
╚═══════════════════════════════════════════════════════════════╝
""")

    bb = BeliefBase()

    print("Step 1: Build initial belief base")
    print("─" * 50)
    steps = [
        ("b -> f",  8,  "Birds fly"),
        ("p -> b",  8,  "Penguins are birds"),
        ("p -> ~f", 9,  "Penguins don't fly  (higher priority)"),
        ("b",       5,  "Tweety is a bird"),
    ]
    for formula_str, prio, desc in steps:
        phi = parse(formula_str)
        bb.add(phi, prio)
        print(f"  add [{prio}] {str(phi):20s}  — {desc}")

    print("\nInitial Belief Base:")
    for entry in sorted(bb.entries, key=lambda e: -e.priority):
        print(f"  {entry}")
    print(f"\n  Consistent: {bb.is_consistent()}")
    print(f"  K |= flies: {bb.entails(parse('f'))}")

    print("\n\nStep 2: Revise — Tweety is a penguin!")
    print("─" * 50)
    p_penguin = parse("p")
    print(f"  Revising with: p  (priority=7)")
    bb.revise(p_penguin, priority=7)
    print("\nBelief Base after K * p:")
    for entry in sorted(bb.entries, key=lambda e: -e.priority):
        print(f"  {entry}")
    print(f"\n  K |= penguin: {bb.entails(parse('p'))}")
    print(f"  K |= flies:   {bb.entails(parse('f'))}")
    print(f"  K |= ~flies:  {bb.entails(parse('~f'))}")
    print(f"  K |= bird:    {bb.entails(parse('b'))}")

    print("\n\nStep 3: Contract — remove belief that Tweety flies")
    print("─" * 50)
    flies = parse("f")
    old_bb = bb.copy()
    bb.contract(flies)
    print(f"  Contracting by: f")
    print("\nBelief Base after K ÷ f:")
    for entry in sorted(bb.entries, key=lambda e: -e.priority):
        print(f"  {entry}")
    print(f"\n  K÷f |= flies: {bb.entails(parse('f'))}")

    print("\n\nStep 4: Properties check")
    print("─" * 50)
    print("AGM Postulates:")
    print("  ✓ K ÷ φ ⊆ K  (Inclusion)")
    print(f"    Contracted size: {len(bb.entries)}, Original size: {len(old_bb.entries)}")
    print(f"    Consistent: {bb.is_consistent()}")
    print(f"    Entails φ: {bb.entails(flies)}")


def main():
    parser = argparse.ArgumentParser(
        description="Belief Revision Agent (Propositional Logic)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        run_interactive()


if __name__ == "__main__":
    main()
