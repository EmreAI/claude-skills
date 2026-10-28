"""Check a deck plan and write a readable deck plan document.

Usage: python3 scripts/check_deck.py deck.json [--plan deck-plan.md]

Checks action titles, wording, limits, variety and sources. Prints the storyline
and open team items. With --plan, also writes the deck plan as Markdown: storyline,
every slide's content with its numbers and sources. Exit code 1 if there are errors.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deckcore import run_check  # noqa: E402

if __name__ == "__main__":
    args = sys.argv[1:]
    plan = None
    if "--plan" in args:
        i = args.index("--plan")
        if i + 1 >= len(args):
            sys.exit(__doc__)
        plan = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        sys.exit(__doc__)
    sys.exit(1 if run_check(args[0], plan=plan)[1] else 0)
