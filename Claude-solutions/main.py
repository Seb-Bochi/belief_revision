#!/usr/bin/env python3
"""
Belief Revision Agent — CLI
Implements both:
  (A) Belief-base revision with partial meet contraction (AGM postulates)
  (B) Plausibility-order revision (lexicographic / minimal revision)

Usage:
    python main.py                      # interactive mode
    python main.py --demo               # run built-in demonstration
    python main.py --agm-test           # run AGM postulate tests
    python main.py --plausibility       # plausibility-order mode demo
"""

import sys
import argparse
from cli import run_interactive, run_demo, run_agm_tests, run_plausibility_demo


def main():
    parser = argparse.ArgumentParser(
        description="Belief Revision Agent (Propositional Logic)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--demo", action="store_true", help="Run built-in demo")
    parser.add_argument("--agm-test", action="store_true", help="Run AGM postulate tests")
    parser.add_argument("--plausibility", action="store_true", help="Run plausibility-order demo")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.agm_test:
        run_agm_tests()
    elif args.plausibility:
        run_plausibility_demo()
    else:
        run_interactive()


if __name__ == "__main__":
    main()
