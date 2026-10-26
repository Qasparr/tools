#!/usr/bin/env python3
# =============================================================================
# "TRVVTH alone has absolute authority." — the charter of the Anchorage
#
# Thelemic date: XXV day of October, Dies Solis, Sol in Scorpio,
# Anno V:xii e.n. (2026 e.v.)
#
# 93.
#
# illuminism/audit.py — the audit harness: PONTIFEX recomputes, TABVLA
# gates, the format is linted against the Teacher's Edition directive,
# and SCRIBA files the case.
#
# By Johnathan 'Qasparr' Monroe (Greek, -ARR, All Rights Reserved,
# Without Prejudice). Released under ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ.
#
# METHOD (Scientific Illuminism): an audit is a set of claims re-weighed
# in the open. Every finding lands in one of three verdicts — PASS
# (verified against the source), FLAG (a discrepancy or a missing
# demanded element, printed and never buried), OPEN (not decidable by
# this instrument; the reason is always stated).
#
# MECHANISM: three passes over the target, each on the Architect's own
# instrument, none re-implemented here:
#   1. PONTIFEX (ptk.weigh): every declared weighing is recomputed in
#      its named bank. Declarations enter by the CONTRACT below — this
#      instrument does not pretend to parse arbitrary prose.
#   2. TABVLA (tabvla.gate): the target's figures, declared in a figures
#      manifest, are built through the Tabvla API and passed through the
#      provenance gate — fail-closed, as the gate is.
#   3. The format lint: lexical checks against the Teacher's Edition
#      header directive (templates/teachers-edition-header.md).
# Findings are then filed as events in a SCRIBA case file (SQLite), with
# SCRIBA's confidence vocabulary mapped from the verdicts, and a Markdown
# audit report is emitted in the Teacher's Edition format.
#
# THE CONTRACT (weighing declarations). A target declares a weighing in
# exactly two ways:
#   (a) an inline declaration line in the Markdown:
#           TERM = N (bank)
#       e.g.  ΘΕΛΗΜΑ = 93 (greek)      עז = 77 (hebrew)
#       bank ∈ {hebrew, hebrew_gadol, greek, latin, agrippa, arabic};
#       table rows (lines starting with |) are data, not declarations;
#   (b) a terms manifest CSV with header  term,declared,bank  passed
#       with --terms.
# Anything that is not a declaration by this contract is prose, and the
# audit says nothing about it. That silence is the honesty of the tool.
#
# DOCTRINE: mark, don't strike. The audit deletes nothing, fixes nothing,
# and buries nothing: FLAGs print in the report and in the case file,
# with the mechanism that produced them, for the red pen.
#
# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
# =============================================================================

"""Audit: recompute the weighings, gate the figures, lint the format."""

import csv
import json
import re
import time
from pathlib import Path

from . import __version__
from .common import (FLAG, OPEN, PASS, RunLog, civil_date, header_block,
                     load_ptk, load_scriba, load_tabvla)

# MECHANISM: one declaration per line, banked at the end of the line.
# The bank vocabulary is closed — an unregistered bank is an OPEN, never
# a guess.
DECL_RE = re.compile(
    r"^\s*(?:[-*]\s+)?(.+?)\s+=\s+(\d+)\s*\(\s*([A-Za-z][A-Za-z_ ]*?)\s*\)\s*$")

BANKS = ("hebrew", "hebrew_gadol", "greek", "latin", "agrippa", "arabic")

# SCRIBA's confidence vocabulary is closed too (attested | reported |
# inferred). MECHANISM of the mapping: PASS = the recomputation was held
# in hand during this run (attested); FLAG = a discrepancy observed and
# recorded, awaiting the red pen (reported); OPEN = a determination the
# instrument deferred (inferred at best).
_CONFIDENCE = {PASS: "attested", FLAG: "reported", OPEN: "inferred"}


# ---------------------------------------------------------------------------
# Pass 1 — PONTIFEX: recompute every declared weighing.
# ---------------------------------------------------------------------------

def _bank_fns(weigh):
    return {"hebrew": weigh.hebrew, "hebrew_gadol": weigh.hebrew_gadol,
            "greek": weigh.greek, "latin": weigh.latin,
            "agrippa": weigh.agrippa, "arabic": weigh.arabic}


def _bank_table(weigh, bank):
    # MECHANISM: the display bank for breakdowns. For hebrew_gadol the
    # final forms take their great values, so the display bank is the
    # hechrechi bank with the gadol finals laid over it — the same sums
    # weigh.hebrew_gadol() produces, letter by letter.
    if bank == "hebrew_gadol":
        merged = dict(weigh.HEBREW)
        merged.update(weigh.HEBREW_GADOL_FINALS)
        return merged
    return {"hebrew": weigh.HEBREW, "greek": weigh.GREEK,
            "latin": weigh.LATIN_ORDINAL, "agrippa": weigh.AGRIPPA,
            "arabic": weigh.ARABIC_ABJAD}[bank]


def _normalize(term, bank):
    # MECHANISM: the banks are keyed as ptk keys them — Greek lowercase,
    # Latin uppercase; Hebrew and Arabic as written.
    if bank == "greek":
        return term.lower()
    if bank in ("latin", "agrippa"):
        return term.upper()
    return term


def recompute(term, declared, bank_name, weigh):
    """Recompute one declared weighing. Returns a finding dict.

    DOCTRINE: the verdict rides on ptk's named bank instrument (e.g.
    weigh.greek()), never on a local re-sum. The per-letter breakdown is
    printed beside it; where the two disagree (the στ mechanism in
    weigh.greek(), which reads the sequence sigma+tau as the stigma
    numeral 6), both numbers stand in the finding with the mechanism
    stated — the red pen adjudicates, the audit does not hide."""
    bank = bank_name.strip().lower().replace(" ", "_")
    if bank not in BANKS:
        return {"term": term, "bank": bank_name, "declared": declared,
                "recomputed": "—", "verdict": OPEN,
                "detail": "unregistered bank %r — the contract's banks are: %s"
                          % (bank_name, ", ".join(BANKS))}
    fn = _bank_fns(weigh)[bank]
    table = _bank_table(weigh, bank)
    norm = _normalize(term, bank)
    got = fn(term)
    pairs, letter_sum = weigh.breakdown(norm, table)
    breakdown = " + ".join("%s %s" % (ch, v) for ch, v in pairs)
    skipped = weigh.unknown(norm, table)
    notes = []
    if skipped:
        notes.append("characters the bank does not weigh (separators): %s"
                     % " ".join(repr(c) for c in skipped))
    if bank == "greek" and letter_sum != got:
        notes.append("mechanism: weigh.greek() reads the sequence στ as the "
                     "stigma numeral (6); the per-letter sum is %d. Both "
                     "numbers stand; the verdict rides on the instrument."
                     % letter_sum)
    if not pairs:
        return {"term": term, "bank": bank, "declared": declared,
                "recomputed": got, "verdict": OPEN,
                "detail": "no letters the %s bank knows — nothing was weighed. %s"
                          % (bank, " ".join(notes))}
    verdict = PASS if got == declared else FLAG
    detail = "%s = %d" % (breakdown, letter_sum if bank != "greek" else got)
    if notes:
        detail += " — " + "; ".join(notes)
    if verdict == FLAG:
        detail += " — DECLARED %d, RECOMPUTED %d" % (declared, got)
    return {"term": term, "bank": bank, "declared": declared,
            "recomputed": got, "verdict": verdict, "detail": detail}


def extract_declarations(text):
    """Pull the inline declarations out of a Markdown target.

    MECHANISM: line scan under DECL_RE; table rows (first non-space
    character |) are data and are skipped, per the contract."""
    decls = []
    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            continue
        m = DECL_RE.match(line)
        if m and len(m.group(1)) <= 80:
            decls.append((m.group(1).strip(), int(m.group(2)), m.group(3)))
    return decls


def load_terms_manifest(path):
    """Read a terms manifest CSV (header: term,declared,bank)."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        out.append((r["term"].strip(), int(r["declared"]), r["bank"].strip()))
    return out


# ---------------------------------------------------------------------------
# Pass 2 — TABVLA: the provenance gate over the declared figures.
# ---------------------------------------------------------------------------

def gate_figures(manifest_path, target_text, out_dir, log):
    """Build the manifest's figures through Tabvla and run the gate.

    Returns a list of (figure-label, verdict, reason) findings.
    MECHANISM: charts are drawn by Tabvla.chart into the audit's output
    directory (the drawing is part of the evidence); images register via
    Tabvla.figure. The gate itself is tabvla.gate — fail-closed: it
    raises on the first figure that cannot point to its numbers, so
    figures after the failure are honestly OPEN (not reached), never
    silently passed."""
    tabvla = load_tabvla()
    if manifest_path is None:
        if "![fig:" in target_text:
            return [("figure references", OPEN,
                     "the target references figures with ![fig: …] but no "
                     "figures manifest was found — a reference carries no "
                     "source, caption, or data, so there is nothing the "
                     "gate can honestly inspect")]
        return [("figures", OPEN,
                 "no figures manifest and no figure references — nothing "
                 "was declared, so nothing is gated")]
    manifest_path = Path(manifest_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = data.get("figures", [])
    scratch = out_dir / "gate-report.md"
    scratch.write_text("# Figure gate\n\n## I. Figures\n", encoding="utf-8")
    t = tabvla.Tabvla(str(scratch))
    labels = []
    for i, entry in enumerate(entries, start=1):
        kind = entry.get("type", "chart")
        label = entry.get("title") or entry.get("image") or ("figure %d" % i)
        labels.append(label)
        try:
            if kind == "chart":
                fig = t.chart(entry.get("kind", "bar"), entry["labels"],
                              entry["values"], title=entry.get("title", ""),
                              source=entry.get("source", ""),
                              out_path=str(out_dir / ("fig-%d.png" % i)))
                fig.caption = entry.get("caption", "")
            else:
                img = entry["image"]
                if not Path(img).is_absolute():
                    img = str(manifest_path.parent / img)
                t.figure(img, caption=entry.get("caption", ""),
                         source=entry.get("source", ""),
                         data=entry.get("data"))
        except Exception as exc:  # malformed entry — mark it, keep going
            labels[-1] = label
            t.figures.append(None)
            log.observe("figure %d (%s) could not be built: %s" % (i, label, exc))
    real = [f for f in t.figures if f is not None]
    findings = []
    failed_at = None
    try:
        tabvla.gate(real)
    except tabvla.ProvenanceError as exc:
        msg = str(exc)
        m = re.match(r"figure (\d+)", msg)
        failed_at = int(m.group(1)) if m else 1
        fail_reason = msg
    else:
        fail_reason = ""
    seen = 0
    for i, entry in enumerate(entries, start=1):
        if t.figures[i - 1] is None:
            findings.append((labels[i - 1], FLAG,
                             "manifest entry could not be built into a figure"))
            continue
        seen += 1
        if failed_at is None:
            findings.append((labels[i - 1], PASS,
                             "gate passed — source, caption, and data ride "
                             "with the figure"))
        elif seen < failed_at:
            findings.append((labels[i - 1], PASS,
                             "passed its checks before the gate closed"))
        elif seen == failed_at:
            findings.append((labels[i - 1], FLAG, fail_reason))
        else:
            findings.append((labels[i - 1], OPEN,
                             "not reached — the gate fails closed at the "
                             "first figure that cannot point to its numbers"))
    return findings


# ---------------------------------------------------------------------------
# Pass 3 — the format lint against the Teacher's Edition directive.
# ---------------------------------------------------------------------------

def _zone_has(text, needle, lo, hi):
    """True if `needle` occurs within the [lo, hi] fraction of the text."""
    start = int(len(text) * lo)
    end = int(len(text) * hi)
    return needle in text[start:end]


def lint_format(text):
    """Lexical checks against templates/teachers-edition-header.md.

    DOCTRINE: the lint checks the MARKS of the format — the standing
    lines and structures the directive demands. It does not judge whether
    the footnotes are genuine or the reasoning sound; that judgment is
    TRVVTH's, exercised by the red pen, and the lint says so."""
    checks = []

    def add(name, verdict, reason):
        checks.append((name, verdict, reason))

    add("Title block (H1)", PASS if re.search(r"^# ", text, re.M) else FLAG,
        "an H1 title opens the document" if re.search(r"^# ", text, re.M)
        else "no H1 title found — the header block opens with the title")
    add("Subtitle", PASS if "A Scientific Illuminist treatment of" in text else FLAG,
        "the Scientific Illuminist subtitle is present" if
        "A Scientific Illuminist treatment of" in text else
        "the subtitle 'A Scientific Illuminist treatment of …' is missing")
    auth = ("Authorship attributed exclusively to Johnathan" in text
            and "All Rights Reserved, Without Prejudice" in text)
    add("Authorship line", PASS if auth else FLAG,
        "the exclusive-authorship line and the ARR/WP notice stand" if auth
        else "the exclusive-authorship line or the ARR/WP notice is missing")
    date_ok = "Anno" in text and "e.n." in text
    add("Thelemic date", PASS if date_ok else FLAG,
        "a Thelemic date line (Anno …, e.n.) is present" if date_ok
        else "no Thelemic date line found")
    cls = all(tok in text for tok in
              ("Enterprise", "Educational", "Research & Development"))
    add("Classification", PASS if cls else FLAG,
        "Enterprise • Educational • Research & Development" if cls
        else "the classification line is incomplete")
    add("Flagpole (front)", PASS if _zone_has(text, "Flagpole of Claim and Coinage", 0.0, 0.30) else FLAG,
        "the Flagpole stands in the first third" if
        _zone_has(text, "Flagpole of Claim and Coinage", 0.0, 0.30) else
        "no Flagpole of Claim and Coinage in the first third of the document")
    add("Flagpole (back)", PASS if _zone_has(text, "Flagpole of Claim and Coinage", 0.70, 1.0) else FLAG,
        "the Flagpole closes the document" if
        _zone_has(text, "Flagpole of Claim and Coinage", 0.70, 1.0) else
        "no Flagpole of Claim and Coinage in the last third of the document")
    romans = re.findall(r"^##\s+(X|IX|IV|V?I{0,3})\.\s", text, re.M)
    add("Roman-numbered sections", PASS if len(romans) >= 2 else FLAG,
        "%d Roman-numbered sections found" % len(romans) if len(romans) >= 2
        else "fewer than two Roman-numbered sections (%d found) — the body "
             "is built in Roman sections" % len(romans))
    tiers = [t for t in ("ATTESTED", "DERIVED", "CONSTRUCTED", "UNCHARTED")
             if t in text]
    add("Tier labels", PASS if tiers else FLAG,
        "tiers present: %s" % ", ".join(tiers) if tiers
        else "no tier labels (ATTESTED / DERIVED / CONSTRUCTED / UNCHARTED) found")
    elems = [w for w in ("Inputs", "Processes", "Outputs", "Tolerances")
             if w in text]
    add("Four-element test", PASS if len(elems) == 4 else FLAG,
        "Inputs, Processes, Outputs, Tolerances all stated" if len(elems) == 4
        else "missing: %s" % ", ".join(
            w for w in ("Inputs", "Processes", "Outputs", "Tolerances")
            if w not in elems))
    add("Table of Authorities",
        PASS if "Table of Authorities" in text else OPEN,
        "a Table of Authorities stands in the document" if
        "Table of Authorities" in text else
        "none found — the directive requires one where applicable; "
        "applicability is the red pen's call, so this stands OPEN")
    if re.search(r"^#+\s+.*Colophon", text, re.M):
        add("Colophon", PASS, "a Colophon section closes the document")
    elif "Colophon" in text:
        add("Colophon", OPEN, "a colophon is named but not headed as a section")
    else:
        add("Colophon", FLAG, "no Colophon — the format closes with one")
    add("Footer spec",
        PASS if "Flagpole of Claim and Coinage reserved" in text else OPEN,
        "the footer line is declared in the document" if
        "Flagpole of Claim and Coinage reserved" in text else
        "footers are applied at compile time (illuminism compile) and "
        "cannot be verified from Markdown source — verify in the PDF")
    add("Closing motto", PASS if "Live, Love, and let Love, Live" in text else FLAG,
        "the motto closes the document" if
        "Live, Love, and let Love, Live" in text else
        "the closing motto 'Live, Love, and let Love, Live.' is missing")
    return checks


# ---------------------------------------------------------------------------
# The verb.
# ---------------------------------------------------------------------------

def resolve_target(target):
    """A document, or a project directory (its README / first Markdown).

    MECHANISM: directory targets resolve to README.md when present, else
    the first *.md in sorted order; the choice is logged, never hidden."""
    p = Path(target)
    if p.is_dir():
        for cand in [p / "README.md"] + sorted(p.glob("*.md")):
            if cand.is_file():
                return cand
        raise FileNotFoundError("no Markdown document in directory %s" % p)
    if not p.is_file():
        raise FileNotFoundError("target not found: %s" % p)
    return p


def run(args, log):
    """illuminism audit — the harness. Returns the process exit code."""
    ptk_pkg = load_ptk()  # puts the toolkit home on sys.path first
    from ptk import table as ptk_table

    weigh_mod = ptk_pkg.weigh
    target = resolve_target(args.target)
    out_dir = Path(args.out) if args.out else target.parent / (target.stem + "-audit")
    out_dir.mkdir(parents=True, exist_ok=True)
    text = target.read_text(encoding="utf-8")

    log.phase("The anchorage", "ptk's banks reproduce their calibration "
              "weighings before anything is weighed on them")
    log.method("weigh.calibrate() from %s" % weigh_mod.__file__)
    weigh_mod.calibrate()
    log.result("calibration holds — עז=77, θελημα=αγαπη=93, AXONEME=77, "
               "CELL=32, gadol אעם=671")

    log.phase("Extraction", "the target declares its weighings by the "
              "contract (inline lines and/or a terms manifest) and by "
              "nothing else")
    decls = extract_declarations(text)
    log.observe("%d inline declaration(s) in %s" % (len(decls), target))
    if args.terms:
        extra = load_terms_manifest(args.terms)
        log.observe("%d declaration(s) from manifest %s" % (len(extra), args.terms))
        decls += extra
    log.result("%d weighing(s) under audit" % len(decls))

    log.phase("PONTIFEX pass", "every declared weighing recomputes in its "
              "named bank; a declaration that matches is a PASS")
    findings = [recompute(t, d, b, weigh_mod) for (t, d, b) in decls]
    for f in findings:
        log.observe("%s (%s): declared %s, recomputed %s — %s"
                    % (f["term"], f["bank"], f["declared"], f["recomputed"],
                       f["verdict"]))
    if not findings:
        log.observe("no declarations — the PONTIFEX pass has nothing to "
                    "recompute (contract silence, stated, not padded)")

    log.phase("TABVLA pass", "the target's figures, declared in a manifest, "
              "pass the provenance gate or the gate's refusal is the finding")
    manifest = args.figures
    if manifest is None:
        beside = target.parent / "figures.json"
        manifest = str(beside) if beside.is_file() else None
    fig_findings = gate_figures(manifest, text, out_dir, log)
    for label, verdict, reason in fig_findings:
        log.observe("figure '%s' — %s: %s" % (label, verdict, reason))

    log.phase("Format lint", "the marks of the Teacher's Edition format "
              "are present where the directive demands them")
    lint = lint_format(text)
    for name, verdict, reason in lint:
        log.observe("%s — %s: %s" % (name, verdict, reason))

    # ---- SCRIBA: file the case -------------------------------------------
    log.phase("The case file", "every finding is filed in SCRIBA with its "
              "confidence, so the audit itself has a provenance")
    scriba = load_scriba()
    case_path = Path(args.case) if args.case else out_dir / "case.db"
    case = scriba.CaseFile(str(case_path))
    today = time.strftime("%Y-%m-%d")
    src = case.add_source(str(target), "document",
                          "illuminism audit %s" % __version__)
    filed = 0
    case.add_event(today, "audit opened: %s" % target.name,
                   "target %s; report in %s" % (target, out_dir), "attested")
    filed += 1
    for f in findings:
        case.add_event(today, "PONTIFEX: %s — %s" % (f["term"], f["verdict"]),
                       f["detail"], _CONFIDENCE[f["verdict"]])
        filed += 1
    for label, verdict, reason in fig_findings:
        case.add_event(today, "TABVLA: %s — %s" % (label, verdict), reason,
                       _CONFIDENCE[verdict])
        filed += 1
    for name, verdict, reason in lint:
        case.add_event(today, "FORMAT: %s — %s" % (name, verdict), reason,
                       _CONFIDENCE[verdict])
        filed += 1
    all_rows = ([("PONTIFEX", f["verdict"]) for f in findings]
                + [("TABVLA", v) for _, v, _ in fig_findings]
                + [("FORMAT", v) for _, v, _ in lint])
    counts = {v: sum(1 for _, x in all_rows if x == v) for v in (PASS, FLAG, OPEN)}
    case.add_event(today, "audit summary",
                   "PASS %d · FLAG %d · OPEN %d" % (counts[PASS], counts[FLAG],
                                                    counts[OPEN]),
                   "attested")
    filed += 1
    case.close()
    log.result("%d event(s) filed in %s" % (filed, case_path))

    # ---- the report --------------------------------------------------------
    log.phase("The report", "the ledgers assemble into the audit report "
              "in the Teacher's Edition format")
    lines = header_block("Audit of %s" % target.name,
                         subject="the audit of %s" % target)
    lines += ["## I. Summary", "",
              "Target: `%s`. Verdicts: **PASS %d · FLAG %d · OPEN %d**. "
              "Nothing was deleted, nothing was auto-fixed; every finding "
              "is marked below and filed in the case file (`%s`)."
              % (target, counts[PASS], counts[FLAG], counts[OPEN], case_path),
              ""]
    lines += ["## II. PONTIFEX — the weighings, recomputed", ""]
    if findings:
        rows = [[f["term"], f["bank"], str(f["declared"]), str(f["recomputed"]),
                 f["verdict"], f["detail"]] for f in findings]
        lines.append(ptk_table.Table(
            ["term", "bank", "declared", "recomputed", "verdict", "breakdown / mechanism"],
            rows).to_markdown())
    else:
        lines += ["No weighings were declared under the contract — the "
                  "pass is silent, and the silence is stated, not padded.", ""]
    lines += ["## III. TABVLA — the figure gate", ""]
    lines.append(ptk_table.Table(
        ["figure", "verdict", "reason"],
        [[label, verdict, reason] for label, verdict, reason in fig_findings]
    ).to_markdown())
    lines += ["## IV. The format lint", ""]
    lines.append(ptk_table.Table(
        ["check", "verdict", "reason"],
        [[name, verdict, reason] for name, verdict, reason in lint]
    ).to_markdown())
    lines += ["## Colophon", "",
              "Generated by illuminism audit %s on %s, over ptk (PONTIFEX), "
              "TABVLA, and VESTIGATOR/SCRIBA — the Architect's own "
              "instruments. Released under ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ."
              % (__version__, civil_date()), "",
              "Authorship attributed exclusively to Johnathan 'Qasparr' "
              "Monroe (Greek, -ARR, All Rights Reserved, Without Prejudice).",
              "", "Method of Science. Aim of Religion.", "",
              "Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, "
              "ARR, All Rights Reserved, Without Prejudice. Right of claim "
              "hereby reserved and coined under the authority of the "
              "Living Man.", "", "93 — Live, Love, and let Love, Live.", ""]
    report_path = out_dir / "audit-report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    log.result("audit report written: %s" % report_path)
    print("audit: PASS %d · FLAG %d · OPEN %d — report: %s"
          % (counts[PASS], counts[FLAG], counts[OPEN], report_path))
    return (1 if counts[FLAG] else 0), report_path

# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
