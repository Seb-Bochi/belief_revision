#!/usr/bin/env python3
"""
Belief Revision Agent — Main Entry Point
Implements AGM belief revision with resolution-based entailment.

Usage:
    python main.py                  # interactive mode
"""

import sys
import argparse
from lark.exceptions import LarkError

from formula import Atom, And, Not, Implies, Or, Iff, Formula
from belief_base import BeliefBase
from logic_parser import parse_formula, parse_command

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
│    contract <formula>         Contract belief base          │
│    revise <formula> [prio]    Revise belief base (Levi)     │
│    entails <formula>          Check if K |= formula         │
│    show                       Display current belief base   │
│    consistent                 Check consistency             │
│    clear                      Clear belief base             │
├─────────────────────────────────────────────────────────────┤
│  OTHER                                                      │
│    help                       Show this help                │
│    quit / exit                Exit                          │
└─────────────────────────────────────────────────────────────┘
"""


def banner():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║        BELIEF REVISION AGENT — Propositional Logic           ║
║  Implements: AGM revision, contraction, expansion,           ║
║             resolution entailment, CNF conversion            ║
╚═══════════════════════════════════════════════════════════════╝
Type 'help' for commands
""")


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

        try:
            command = parse_command(line)
            cmd = command[0]

            match cmd:
                case "quit" | "exit":
                    print("Goodbye.")
                    break

                case "help":
                    print(HELP_TEXT)

                case "show":
                    print("\nCurrent Belief Base:")
                    if bb.is_empty():
                        print("  (empty)")
                    else:
                        for entry in sorted(bb.entries, key=lambda e: -e.priority):
                            print(f"  {entry}")
                    print()

                case "consistent":
                    result = bb.is_consistent()
                    print(f"  Belief base is {'consistent ✅' if result else 'INCONSISTENT ❌'}")

                case "clear":
                    bb = BeliefBase()
                    print("  Belief base cleared.")

                case "add":
                    _, phi, prio = command
                    bb.add(phi, prio)
                    print(f"  Added: {phi}  (priority={prio})")
                    print(f"  Belief base now has {len(bb.entries)} formula(s).")

                case "contract":
                    _, phi = command
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

                case "revise":
                    _, phi, prio = command
                    bb.revise(phi, prio)

                    print(f"  Revised by: {phi}  (priority={prio})")
                    print("\nBelief Base after revision:")

                    if bb.is_empty():
                        print("  (empty)")
                    else:
                        for entry in sorted(bb.entries, key=lambda e: -e.priority):
                            print(f"  {entry}")

                case "entails":
                    _, phi = command
                    result = bb.entails(phi)
                    print(f"  K |= {phi} : {'Yes ✅' if result else 'No ❌'}")

                case _:
                    print(f"  Unknown command: {cmd}  (type 'help' for commands)")

        except (LarkError, ValueError) as e:
            print(f"  Parse error: {e}")
        except Exception as e:
            print(f"  Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Belief Revision Agent (Propositional Logic)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    run_interactive()


if __name__ == "__main__":
    main()
