#!/usr/bin/env python3
# =============================================================================
# weigh_spread.py -- weigh one word across every ptk bank, audit the skips,
# and test for genuine two-bank bridges.
#
# By the PONTIFEX 777 gap-filling operation, worker-15 (2026-10-13).
# GENERAL tool: usable on any word in any project, not just 777 work.
#
# METHOD (Scientific Illuminism):
#   Weighs WORD in LATIN-ordinal, AGRIPPA, HEBREW (mispar hechrechi) and
#   HEBREW-gadol. unknown() is run on every bank so skipped characters are
#   visible -- a weighing is only honest if its skips are visible.
#
# DOCTRINE (settled with Johnathan):
#   - Hebrew is the proper fallback for tongues with no table; the Hebrew
#     weighing of a transliteration is CONSTRUCTED tier (a hypothesis).
#   - hechrechi vs gadol agreement is NOT a bridge: same bank, two final-
#     letter conventions. Conflating them is how phantom discrepancies
#     are born. This script refuses to report it as one.
#   - A bridge needs TWO honest banks agreeing on the SAME word.
#
# Usage: weigh_spread.py WORD [HEBREW_TRANSLITERATION]
# Example: weigh_spread.py SOL סול
#
# "Live, Love, and let Love, Live." -- 93.
# =============================================================================

import sys

sys.path.insert(0, "/home/hatch/workspace/pontifex/tools")
from ptk.weigh import (latin, agrippa, hebrew, hebrew_gadol,
                       LATIN_ORDINAL, AGRIPPA, HEBREW,
                       unknown, breakdown)


def weigh_spread(word, hebrew_translit=None):
    """MECHANISM: return [(bank, value, tier, skipped), ...] for the word."""
    rows = []
    for bank_name, fn, bank_dict, tier in [
        ("LATIN-ordinal", lambda: latin(word), LATIN_ORDINAL, "attested"),
        ("AGRIPPA", lambda: agrippa(word), AGRIPPA, "attested"),
    ]:
        rows.append((bank_name, fn(), tier, unknown(word.upper(), bank_dict)))
    if hebrew_translit:
        rows.append(("HEBREW-fallback", hebrew(hebrew_translit), "constructed",
                     unknown(hebrew_translit, HEBREW)))
        rows.append(("HEBREW-gadol", hebrew_gadol(hebrew_translit), "constructed",
                     unknown(hebrew_translit, HEBREW)))
    return rows


def find_bridges(rows):
    """MECHANISM: same value in two HONEST banks = bridge candidate.

    DOCTRINE: the hechrechi/gadol pair is excluded -- one bank, two
    conventions, never a bridge."""
    by_value = {}
    for bank, value, tier, skipped in rows:
        key = "HEBREW" if bank.startswith("HEBREW") else bank
        by_value.setdefault(value, set()).add(key)
    return {v: sorted(b) for v, b in by_value.items() if len(b) > 1}


def main(argv):
    if len(argv) < 2:
        print(__doc__.splitlines()[-6])
        return 2
    word = argv[1]
    translit = argv[2] if len(argv) > 2 else None
    rows = weigh_spread(word, translit)
    print(f"word: {word}" + (f"  (hebrew: {translit})" if translit else ""))
    for bank, value, tier, skipped in rows:
        note = f"  skipped={skipped}" if skipped else ""
        print(f"  {bank:15s} = {value:5d}  [{tier}]{note}")
    bridges = find_bridges(rows)
    if bridges:
        for value, banks in bridges.items():
            print(f"  ** BRIDGE: {value} across {banks}")
    else:
        print("  no two-bank bridge")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
