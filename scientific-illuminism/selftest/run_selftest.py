#!/usr/bin/env python3
# =============================================================================
# "The proof is in the running." — after the old saw
#
# Thelemic date: XXV day of October, Dies Solis, Sol in Scorpio,
# Anno V:xii e.n. (2026 e.v.)
#
# 93.
#
# selftest/run_selftest.py — the shipped proof of ΕΠΙΣΤΗΜΟΝΙΚΟΣ
# ΙΛΛΟΥΜΙΝΙΣΜΟΣ: the fixture through all three verbs, the gate's
# refusal exercised as a negative control, and the CLI's own banner
# checked. Run it with:  python3 run_selftest.py   (or: illuminism
# selftest). Exit 0 only when every check passes.
#
# By Johnathan 'Qasparr' Monroe (Greek, -ARR, All Rights Reserved,
# Without Prejudice). Released under ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ.
#
# METHOD (Scientific Illuminism): the self-test calls the verb modules
# exactly as the CLI does (same argument namespaces, same RunLog), then
# asserts on the artifacts — files on disk, rows in the case file, text
# extracted from the compiled PDF. A check that cannot run is reported
# as a failure with its reason, never skipped in silence.
#
# MECHANISM: outputs land in selftest/outputs/ (rebuilt each run); the
# per-verb ultra-verbose run logs are written beside the outputs
# exactly where the CLI writes them; a SELFTEST-RESULTS.md summary is
# written at the end.
#
# DOCTRINE: the negative control is part of the proof. A gate that has
# never been seen to refuse has not been tested; the fixture feeds it
# a figure with no source and a figure whose numbers do not match its
# labels, and demands the refusal both times.
#
# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
# =============================================================================

"""Run the illuminism fixture through all three verbs; assert; report."""

import subprocess
import sys
from argparse import Namespace
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(PKG))

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print("%-58s %s %s" % (name, "PASS" if ok else "FAIL", detail))
    return bool(ok)


def main():
    import shutil
    out = HERE / "outputs"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    from illuminism import audit, compile as compile_mod, report
    from illuminism.common import (RunLog, load_ptk, load_scriba,
                                   load_tabvla)

    # ---- 0. the instruments are alive -----------------------------------
    log = RunLog("selftest", ["run_selftest.py"])
    log.phase("Calibration", "the instruments answer before any verb runs")
    log.method("ptk weigh.calibrate(); TABVLA and SCRIBA imports")
    try:
        weigh = load_ptk().weigh
        check("ptk calibration (עז=77, θελημα=93, AXONEME=77)",
              weigh.calibrate() is True)
        tabvla = load_tabvla()
        check("TABVLA import + gate present",
              hasattr(tabvla, "gate") and hasattr(tabvla, "Tabvla"))
        scriba = load_scriba()
        check("VESTIGATOR SCRIBA import", hasattr(scriba, "CaseFile"))
    except Exception as exc:  # the instruments must load; anything else is noise
        check("instrument load", False, repr(exc))
        return _finish(out, log)

    # ---- 1. audit ---------------------------------------------------------
    log.phase("Audit", "the fixture's declarations recompute, its figure "
              "gates, its format lints clean")
    alog = RunLog("audit", ["audit", str(HERE / "fixture.md")])
    code, primary = audit.run(Namespace(
        target=str(HERE / "fixture.md"), terms=None,
        figures=str(HERE / "figures.json"),
        out=str(out / "audit"), case=None), alog)
    alog.write(out / "audit" / "run-log.md")
    check("audit exits 0 (no FLAG)", code == 0, "exit %d" % code)
    check("audit report written", (out / "audit" / "audit-report.md").is_file())
    case_db = out / "audit" / "case.db"
    check("SCRIBA case file written", case_db.is_file())
    if case_db.is_file():
        cf = scriba.CaseFile(str(case_db))
        events = cf.timeline()
        cf.close()
        check("case file timeline is populated", len(events) >= 20,
              "%d events" % len(events))

    # ---- 2. the gate refuses (negative control) ---------------------------
    log.phase("Gate negative control", "a figure with no source, and a "
              "figure whose numbers disagree with its labels, must both "
              "be refused")
    from tabvla.figures import Figure
    refused = 0
    for fig in (Figure(image_path="ghost.png", caption="a caption",
                       source=""),
                Figure(image_path="ghost.png", caption="a caption",
                       source="a source", data={"labels": ["a", "b"],
                                                 "values": [1]})):
        try:
            tabvla.gate([fig])
        except tabvla.ProvenanceError:
            refused += 1
    check("gate refuses both dishonest figures", refused == 2,
          "%d/2 refused" % refused)

    # ---- 3. report ----------------------------------------------------------
    log.phase("Report", "the CSV becomes tables, a gated figure, and an "
              "illustrated PDF")
    rlog = RunLog("report", ["report", str(HERE / "data.csv")])
    code, primary = report.run(Namespace(
        data=str(HERE / "data.csv"), out=str(out / "report"), title=None),
        rlog)
    rlog.write(out / "report" / "run-log.md")
    check("report exits 0", code == 0, "exit %d" % code)
    check("report Markdown written",
          (out / "report" / "data-report.md").is_file())
    rpdf = out / "report" / "data-report.pdf"
    check("report PDF written (gate passed)", rpdf.is_file()
          and rpdf.stat().st_size > 5000,
          "%d bytes" % (rpdf.stat().st_size if rpdf.is_file() else 0))

    # ---- 4. compile ---------------------------------------------------------
    log.phase("Compile", "the fixture compiles to a Teacher's Edition PDF "
              "whose footers resolve")
    clog = RunLog("compile", ["compile", str(HERE / "fixture.md")])
    code, pdf_path = compile_mod.run(Namespace(
        document=str(HERE / "fixture.md"),
        out=str(out / "fixture.pdf"), title=None), clog)
    clog.write(out / "run-log.md")
    check("compile exits 0", code == 0, "exit %d" % code)
    if pdf_path and Path(pdf_path).is_file():
        import re
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
        check("compiled PDF has >= 2 pages", len(reader.pages) >= 2,
              "%d pages" % len(reader.pages))
        check("Flagpole footer text present in the print",
              "Flagpole of Claim and Coinage reserved" in text)
        check("— N of M — footers resolve",
              bool(re.search(r"—\s*\d+\s*of\s*\d+\s*—", text)))
        check("no unresolved {nb} alias in the print", "{nb}" not in text)
    else:
        check("compiled PDF written", False, "no output")

    # ---- 5. the CLI itself ---------------------------------------------------
    log.phase("CLI", "the executable door answers with the Greek banner")
    proc = subprocess.run(
        [sys.executable, str(PKG / "bin" / "illuminism"), "--help"],
        capture_output=True, text=True)
    check("bin/illuminism --help exits 0", proc.returncode == 0)
    check("Greek masthead in the help",
          "ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ" in proc.stdout)
    check("all three verbs in the help",
          all(v in proc.stdout for v in ("audit", "report", "compile")))

    return _finish(out, log)


def _finish(out, log):
    failed = [r for r in RESULTS if not r[1]]
    lines = ["# SELFTEST RESULTS — illuminism 0.1.0", "",
             "Released under ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ.", "",
             "| Check | Verdict | Detail |", "|---|---|---|"]
    for name, ok, detail in RESULTS:
        lines.append("| %s | %s | %s |"
                     % (name, "PASS" if ok else "FAIL", detail))
    lines += ["", "**%d/%d checks passed.**"
              % (len(RESULTS) - len(failed), len(RESULTS)), ""]
    (out / "SELFTEST-RESULTS.md").write_text("\n".join(lines),
                                             encoding="utf-8")
    log.result("selftest: %d/%d checks passed"
               % (len(RESULTS) - len(failed), len(RESULTS)))
    log.write(out / "selftest-run-log.md")
    print("\nSELFTEST: %s (%d/%d)"
          % ("ALL PASS" if not failed else "FAILURES PRESENT",
             len(RESULTS) - len(failed), len(RESULTS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
