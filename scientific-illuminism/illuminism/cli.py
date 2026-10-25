#!/usr/bin/env python3
# =============================================================================
# "Do what thou wilt shall be the whole of the Law — and let the log
#  be the witness of what was done."
#
# Thelemic date: XXV day of October, Dies Solis, Sol in Scorpio,
# Anno V:xii e.n. (2026 e.v.)
#
# 93.
#
# illuminism/cli.py — the door of the house: three verbs and a proof.
#
#     illuminism audit   <target>   recompute, gate, lint, file the case
#     illuminism report  <data>     tables + gated figures -> report
#     illuminism compile <doc.md>   Markdown -> Teacher's Edition PDF
#     illuminism selftest           run the shipped proof, end to end
#
# By Johnathan 'Qasparr' Monroe (Greek, -ARR, All Rights Reserved,
# Without Prejudice). Released under ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ.
#
# METHOD (Scientific Illuminism): the CLI is a dispatcher, nothing more.
# Each verb module carries its own doctrine and writes its own
# ultra-verbose run log (common.RunLog) beside its primary output, so a
# run can be re-weighed from its log alone.
#
# MECHANISM: argparse subcommands. Exit codes — 0: the run completed
# with no FLAG; 1: the run completed and FLAGged (audit findings, or a
# gate refusal in report); 2: the run could not start (missing target,
# unsupported input). A traceback is a bug, never a verdict: unexpected
# exceptions are reported as errors, not dressed as findings.
#
# DOCTRINE: the banner is the release name in Greek, because the
# release is the name. ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ — and its weighing,
# where printed, is CONSTRUCTED (see README.md).
#
# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
# =============================================================================

"""The illuminism command line: audit, report, compile, selftest."""

import argparse
import subprocess
import sys
from pathlib import Path

from . import GREEK_TITLE, __version__
from .common import RunLog

BANNER = ("%s — Scientific Illuminism, version %s.\n"
          "Report, audit, and compile anything, on the Architect's own "
          "instruments:\nPONTIFEX weighs (ptk), TABVLA draws and gates, "
          "VESTIGATOR's SCRIBA keeps the case file."
          % (GREEK_TITLE, __version__))


def build_parser():
    p = argparse.ArgumentParser(
        prog="illuminism",
        description=BANNER,
        epilog="Released under ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ. "
               "Live, Love, and let Love, Live. — 93.")
    p.add_argument("--version", action="version",
                   version="illuminism %s (%s)" % (__version__, GREEK_TITLE))
    sub = p.add_subparsers(dest="command")

    a = sub.add_parser("audit", help="recompute the weighings (ptk), gate "
                       "the figures (TABVLA), lint the Teacher's Edition "
                       "format, file the case (SCRIBA)")
    a.add_argument("target", help="a Markdown document, or a project "
                   "directory (its README / first Markdown file)")
    a.add_argument("--terms", help="terms manifest CSV (term,declared,bank) "
                   "with further declared weighings")
    a.add_argument("--figures", help="figures manifest JSON (default: "
                   "figures.json beside the target, when present)")
    a.add_argument("--out", help="output directory (default: "
                   "<target-stem>-audit beside the target)")
    a.add_argument("--case", help="SCRIBA case file (default: case.db in "
                   "the output directory)")

    r = sub.add_parser("report", help="structured data (CSV/JSON) -> "
                       "Teacher's-Edition-format report with gated figures")
    r.add_argument("data", help="a CSV or JSON data file (contracts in "
                   "the README and in report.py's header)")
    r.add_argument("--out", help="output directory (default: "
                   "<data-stem>-report beside the data)")
    r.add_argument("--title", help="report title (default: from the data)")

    c = sub.add_parser("compile", help="Markdown -> finished Teacher's "
                       "Edition PDF (resolving — N of M — Flagpole footers)")
    c.add_argument("document", help="the Markdown document")
    c.add_argument("--out", help="output PDF (default: beside the "
                   "document, same stem)")
    c.add_argument("--title", help="title for a scaffolded title page "
                   "(fragments only)")

    sub.add_parser("selftest", help="run the shipped fixture through all "
                   "three verbs and print the proof")
    return p


def _selftest():
    """MECHANISM: the self-test is a separate program on purpose — it
    drives the CLI the way a reader would, in a fresh interpreter."""
    script = (Path(__file__).resolve().parent.parent
              / "selftest" / "run_selftest.py")
    if not script.is_file():
        print("illuminism: selftest script not found at %s" % script)
        return 2
    return subprocess.call([sys.executable, str(script)])


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    if args.command == "selftest":
        return _selftest()

    from . import audit, compile as compile_mod, report
    runners = {"audit": audit.run, "report": report.run,
               "compile": compile_mod.run}
    log = RunLog(args.command, argv)
    try:
        code, primary = runners[args.command](args, log)
    except FileNotFoundError as exc:
        print("illuminism: %s" % exc)
        log.note("run could not start: %s" % exc)
        fallback = Path("illuminism-%s-run-log.md" % args.command)
        log.write(fallback)
        print("illuminism: run log written to %s" % fallback)
        return 2
    if primary is not None:
        log_path = Path(primary).parent / "run-log.md"
        log.write(log_path)
        print("illuminism: run log: %s" % log_path)
    return code


if __name__ == "__main__":
    sys.exit(main())

# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
