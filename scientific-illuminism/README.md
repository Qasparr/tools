# ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ

**Scientific Illuminism** — an orchestrator that **reports, audits, and
compiles anything**, built entirely on Johnathan 'Qasparr' Monroe's own
authored instruments. One command line, three verbs:

```console
$ illuminism audit   <target>     # recompute, gate, lint, file the case
$ illuminism report  <data>       # data -> tables + gated figures -> report
$ illuminism compile <doc.md>     # Markdown -> Teacher's Edition PDF
$ illuminism selftest             # the shipped proof, run end to end
```

> **The weighing of the title (CONSTRUCTED).** ΕΠΙΣΤΗΜΟΝΙΚΟΣ
> ΙΛΛΟΥΜΙΝΙΣΜΟΣ weighed in the Greek Milesian bank, letter by letter
> (ptk): ΕΠΙΣΤΗΜΟΝΙΚΟΣ = 1063, ΙΛΛΟΥΜΙΝΙΣΜΟΣ = 1160 — **2223**. Under
> ptk's `greek()` rule, which reads the sequence στ as the single
> numeral stigma (6) rather than σ (200) + τ (300), the first word
> weighs 569 and the title **1729**. Both readings are printed because
> the mechanism differs; neither is doctrine. ΙΛΛΟΥΜΙΝΙΣΜΟΣ is a modern
> transliteration with no classical bank, so any weighing of the title
> is **CONSTRUCTED** — a free choice, labeled as one, never attested.

## The instruments

`illuminism` re-implements nothing. It orchestrates three toolkits the
Architect already authored, each in its settled home:

| Instrument | Home | What it does here |
|---|---|---|
| **PONTIFEX toolkit (ptk 0.1.0)** | `~/workspace/pontifex/tools/` | weighs every declared term in its own tongue's bank (Hebrew, Hebrew gadol, Greek, Latin ordinal, Agrippa, Arabic abjad) and renders the ledgers as tables |
| **TABVLA 0.1.0** | `~/workspace/tabvla/` | draws every figure and stands its provenance gate over them — fail-closed: a figure that cannot point to its numbers does not ship |
| **VESTIGATOR / SCRIBA 0.1.0** | `~/workspace/vestigator/` | keeps the audit's case file (SQLite): every finding filed as an event, confidence mandatory |
| **INDAGATOR** | (same repo) | the hunt engine — *not* used here, stated plainly: an audit consumes found material, it does not hunt. Forcing it in would be decoration, not engineering. |

Discovery: the toolkits are found in their workspace homes by default
and can be pointed elsewhere with `ILLUMINISM_PTK_HOME`,
`ILLUMINISM_TABULA_HOME`, `ILLUMINISM_VESTIGATOR_HOME`.

SCRIBA fits the audit honestly and only there: an audit *is* a case —
claims examined, findings filed with confidence. Nothing about the
orchestrator is artificial: report uses TABVLA + ptk tables, compile
uses the house fpdf2 pattern, and each verb's own module header states
its mechanism and doctrine in full.

## Running it

No install needed — the executable wrapper carries its own path:

```console
$ ~/workspace/tools/scientific-illuminism/bin/illuminism --help
```

Or install the package (console script `illuminism`):

```console
$ pip install ~/workspace/tools/scientific-illuminism
```

Python dependencies beyond the Architect's toolkits: `matplotlib` and
`fpdf2` (TABVLA's and the house builders' deps). Optional: `pypdf`
(compile's footer verification — without it the check stands OPEN in
the log, stated, not skipped) and `uharfbuzz` (compile's text shaping —
without it the compiler degrades to unshaped text and says so).

**Every run writes an ultra-verbose log** (`run-log.md` beside the
primary output): hypothesis → method → observation → result, per the
standing order. Exit codes: **0** clean · **1** completed with FLAGs
(or a gate refusal) · **2** could not start.

## `illuminism audit <target>`

The target is a Markdown document, or a project directory (its
`README.md`, else its first Markdown file — the choice is logged).
Three passes, one report (`<target-stem>-audit/audit-report.md`), and
the case filed in SCRIBA (`case.db` beside the report):

**(a) PONTIFEX — every declared weighing, recomputed.** The extraction
contract is explicit and deliberately narrow; the audit does **not**
pretend to parse prose. A weighing is in contract when it is declared
as:

- an inline line of the form `TERM = N (bank)` in the document
  (an optional leading bullet is allowed; table rows are data, not
  declarations), where *bank* ∈ `hebrew`, `hebrew_gadol`, `greek`,
  `latin`, `agrippa`, `arabic`; or
- a row of a terms manifest CSV (`--terms`, header `term,declared,bank`).

Each declaration is recomputed with ptk's bank function and printed
with its per-letter breakdown. Verdicts: **PASS** at exact equality,
**FLAG** on mismatch (declared and recomputed both printed), **OPEN**
when the bank is unregistered or the term has no weighable letters.
One mechanism is printed wherever it bites: ptk's `greek()` reads στ
as the stigma numeral (6); when a Greek term's letter-sum differs from
the bank function's result for that reason, both numbers stand.

**(b) TABVLA — the provenance gate over the target's figures.** Figures
are declared in a manifest (`figures.json` beside the target, or
`--figures`): entries of `{"type": "chart", kind, labels, values,
title, source, caption}` (drawn by TABVLA) or `{"type": "image", image,
source, caption, data}`. The gate runs fail-closed; figures before a
refusal keep their PASS (they passed their checks), the refused figure
is FLAGged with the gate's own words, later figures stand OPEN —
*not reached*. A document with `![fig: …]` references but no manifest
is OPEN: the audit will not invent numbers for a drawing.

**(c) The Teacher's Edition format lint** against
`~/workspace/templates/teachers-edition-header.md`: H1 title block ·
subtitle · authorship line · Thelemic date · classification ·
Flagpole front (first third) and back (last third) · ≥ 2
Roman-numbered sections · tier labels present · the four elements
(Inputs, Processes, Outputs, Tolerances) · Table of Authorities
(absent → OPEN, *where applicable*) · Colophon · footer spec ·
closing motto. Each check prints its reason.

Nothing is deleted and nothing is auto-fixed. Findings are marked —
in the report, in the log, and in the SCRIBA case file, where PASS
files as *attested*, FLAG as *reported*, OPEN as *inferred*
(SCRIBA's confidence vocabulary, mapped, not bent).

## `illuminism report <data>`

Structured data in, a Teacher's-Edition-format report out — the data
as ptk tables **and** as TABVLA figures, gated, in Markdown
(`<stem>-report.md`, the primary artifact) and as an illustrated PDF.
Contracts, both stated, neither guessed:

- **CSV** — header row required; column 1 is the label column; each
  further column is a series, charted only if fully numeric (a column
  that fails is dropped from the figures, kept in the printed table,
  and the drop is logged — marked, never repaired).
- **JSON** — the *charts shape* `{"title", "charts": [{kind, title,
  labels, values, source, caption}]}` or the *TABVLA results shape*
  `{"title", "tables": [{caption, headers, rows}]}` (labels from
  column 1, values from the last column when fully numeric).

Every figure's caption and the report's appendix print the exact
numbers it was drawn from. If the gate refuses a figure, no PDF ships
and the refusal is the result (exit 1).

## `illuminism compile <document.md>`

Markdown in, the finished Teacher's Edition PDF out — fpdf2, in the
lineage of the house builders (`ptk/scripts/twelve-tongues/
build_report_pdf.py`), extended where the format demands more:

- the **Flagpole footer resolves — N of M —** on every page (fpdf2's
  page-count alias in `footer()`, not a post-hoc stamp), and the claim
  is *verified after rendering*: the PDF is re-opened and the footer
  text checked in the extracted text;
- the **Doctrine logo** (`~/workspace/templates/doctrine-logo.png`)
  heads the print when the file exists; its absence degrades
  gracefully and is noted in the log and in any scaffolded colophon;
- **scaffolding, only where lacking**: a title page for fragments
  (no H1), a Table of Authorities gathered from the document's own
  citations (when it cites nothing, the section prints the dry-well
  sentence — stated, never padded), and a Colophon carrying the
  generation note, *"Released under ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ"*,
  the exclusive authorship, the Flagpole, and the motto. Every
  addition is logged line by line.

The renderer speaks the house Markdown subset — headings, rules,
bullets, numbered items, tables, paragraphs with **bold** and
*italic*, figure lines `![fig: path]` / `![alt](path)` — and nothing
beyond it.

## The self-test (the shipped proof)

`selftest/` carries a fixture that exercises all three verbs end to
end: `fixture.md` (a complete Teacher's Edition document declaring
eight weighings in five banks), `figures.json` (one chart to gate),
`data.csv` (a series to report). Run it:

```console
$ illuminism selftest          # or: python3 selftest/run_selftest.py
```

Outputs land in `selftest/outputs/` — the audit report and its SCRIBA
case file, the report Markdown + PDF, the compiled PDF, every run
log, and `SELFTEST-RESULTS.md`. Results from the release run
(2026-10-25, this host):

| Verb | Result |
|---|---|
| audit | **PASS 23 · FLAG 0 · OPEN 0** — 8 weighings recomputed exact, 1 figure gated, 14 format checks passed; case file holds 25 events |
| gate (negative control) | **2/2 refused** — a figure with no source, and a figure whose values disagree with its labels, both turned away by the gate |
| report | Markdown + illustrated PDF (68,589 bytes) from `data.csv` |
| compile | 2-page PDF; Flagpole footer present and **— N of M — resolved** in the extracted text; no `{nb}` left behind |
| CLI | `--help` exits 0 under the Greek masthead, all three verbs listed |

**19/19 checks passed.** A dirty-fixture run (one declared value
falsified, the Colophon removed) was also exercised by hand: exit 1,
the falsified weighing FLAGged with declared *and* recomputed values,
the Colophon FLAGged — marked, never struck.

## OPEN limitations (stated, not hidden)

- **Extraction is contract-bound by design.** The audit recomputes
  weighings declared in the contract form only. A weighing buried in
  prose is invisible to it — the contract is the honesty.
- **The format lint is lexical, not semantic.** It verifies that the
  format's pieces stand where the format puts them; it does not judge
  whether a Colophon *says* anything true.
- **Compile renders the house Markdown subset.** Raw HTML, nested
  lists, and code fences are outside the subset and render as text.
- **No ephemeris is bundled**, so no Thelemic date is ever computed:
  civil dates are used and labeled civil; the Thelemic date remains
  the scribe's pen — in the audit report's header, in scaffolded
  title pages, everywhere this package prints a date.
- **Report's PDF is TABVLA's Letter assembly**; the Markdown report is
  the primary artifact and carries the full format.
- **Audit's figure pass checks the manifest's figures**, not images
  embedded in foreign formats; `![fig: …]` references without a
  manifest stand OPEN by design.
- **INDAGATOR is unused** (see the instruments table).

---

*Authorship attributed exclusively to Johnathan 'Qasparr' Monroe
(Greek, -ARR, All Rights Reserved, Without Prejudice).*

*Method of Science. Aim of Religion.*

*Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, All
Rights Reserved, Without Prejudice. Right of claim hereby reserved and
coined under the authority of the Living Man.*

*93 — Live, Love, and let Love, Live.*
