#!/usr/bin/env python3
# =============================================================================
# "A figure that cannot point to its numbers does not ship."
# — the TABVLA doctrine
#
# Thelemic date: XXV day of October, Dies Solis, Sol in Scorpio,
# Anno V:xii e.n. (2026 e.v.)
#
# 93.
#
# illuminism/report.py — structured data in, a Teacher's-Edition-format
# report out: the data as tables (ptk.table), the data as figures
# (TABVLA, gated), and the numbers printed beside the drawings so any
# reader can check any bar against its list.
#
# By Johnathan 'Qasparr' Monroe (Greek, -ARR, All Rights Reserved,
# Without Prejudice). Released under ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ.
#
# METHOD (Scientific Illuminism): the report invents nothing. Every
# number in it is a number in the input file; every figure is built by
# TABVLA from those numbers and passes TABVLA's provenance gate before
# the illustrated PDF assembles — the gate fails closed, and so does
# this verb.
#
# THE CONTRACT (input data). Two shapes are read, both stated, neither
# guessed:
#   CSV — a header row is required. Column 1 is the label column; every
#         further column is a series. A series is charted only if every
#         non-empty cell in it is numeric; a column that fails that test
#         is dropped and the drop is logged (marked, never repaired).
#   JSON — either the charts shape:
#           {"title": …, "charts": [{"kind": "bar|line|scatter",
#             "title": …, "labels": […], "values": […],
#             "source": …, "caption": …}]}
#         or the TABVLA results shape:
#           {"title": …, "tables": [{"caption": …, "headers": […],
#             "rows": [[…]]}]}
#         (labels from column 1, values from the last column, charted
#         when that column is fully numeric).
#
# MECHANISM: the Markdown report is assembled first (header block from
# the directive, the data as ptk tables, figure references, an appendix
# of figures-and-numbers, a colophon). TABVLA then ingests that very
# Markdown, draws the charts from the same numbers, gates them, and
# assembles the illustrated PDF. One data path, two mouths — they
# cannot disagree.
#
# DOCTRINE: the Markdown report is the primary artifact; the PDF is its
# illustrated twin. If the gate refuses a figure, no PDF ships and the
# refusal is the result.
#
# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
# =============================================================================

"""Report: data -> tables + gated figures -> Teacher's Edition report."""

import csv
import json
from pathlib import Path

from . import __version__
from .common import (FLAG, PASS, civil_date, header_block, load_ptk,
                     load_tabula)


def _num(cell):
    """Parse a cell as a number; None when it is not one.

    MECHANISM: integral floats return as int (77, not 77.0) so the
    printed numbers match the weighed world they usually describe."""
    try:
        v = float(str(cell).strip())
    except (TypeError, ValueError):
        return None
    return int(v) if v == int(v) else v


def read_csv_series(path):
    """CSV contract -> (title_tables, series list).

    Returns (raw_table, series): raw_table = (headers, rows) as strings
    for the printed table; series = [{name, labels, values}]."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    if len(rows) < 2:
        raise ValueError("CSV needs a header row and at least one data row")
    headers, body = rows[0], rows[1:]
    labels = [r[0] for r in body]
    series = []
    dropped = []
    for ci, name in enumerate(headers[1:], start=1):
        values, ok = [], True
        for r in body:
            cell = r[ci] if ci < len(r) else ""
            if str(cell).strip() == "":
                ok = False
                break
            v = _num(cell)
            if v is None:
                ok = False
                break
            values.append(v)
        if ok:
            series.append({"name": name, "labels": labels, "values": values,
                           "kind": "bar"})
        else:
            dropped.append(name)
    return (headers, body), series, dropped


def read_json_series(path):
    """JSON contracts -> (title, tables, series)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    title = data.get("title", "")
    tables, series = [], []
    if "charts" in data:
        for ch in data["charts"]:
            series.append({"name": ch.get("title", "chart"),
                           "labels": [str(x) for x in ch["labels"]],
                           "values": ch["values"],
                           "kind": ch.get("kind", "bar"),
                           "source": ch.get("source", ""),
                           "caption": ch.get("caption", "")})
    elif "tables" in data:
        for tb in data["tables"]:
            headers = [str(h) for h in tb["headers"]]
            rows = [[str(c) for c in r] for r in tb["rows"]]
            tables.append((tb.get("caption", "data"), headers, rows))
            values = [_num(r[-1]) for r in tb["rows"]]
            if values and all(v is not None for v in values):
                series.append({"name": tb.get("caption", "data"),
                               "labels": [str(r[0]) for r in tb["rows"]],
                               "values": values, "kind": "bar"})
    else:
        raise ValueError("unrecognized JSON shape — the contract is the "
                         "charts shape or the TABVLA results shape "
                         "(see the module header)")
    return title, tables, series


def _pairs(labels, values, limit=10):
    """'a = 1, b = 2, …' — the numbers beside the drawing."""
    parts = ["%s = %s" % (l, v) for l, v in zip(labels, values)]
    if len(parts) > limit:
        parts = parts[:limit] + ["… (%d more)" % (len(parts) - limit)]
    return ", ".join(parts)


def run(args, log):
    """illuminism report — build the report. Returns the exit code."""
    ptk_pkg = load_ptk()
    ptk_table = ptk_pkg.table
    tabula = load_tabula()

    data_path = Path(args.data)
    if not data_path.is_file():
        print("report: data file not found: %s" % data_path)
        return 2, None
    out_dir = Path(args.out) if args.out else data_path.parent / (data_path.stem + "-report")
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = data_path.stem

    log.phase("Ingest", "the input file carries every number the report "
              "will print — the report invents nothing")
    log.method("contract read of %s (%s)" % (data_path, data_path.suffix))
    tables = []   # [(caption, headers, rows)] for section I
    if data_path.suffix.lower() == ".csv":
        (headers, body), series, dropped = read_csv_series(data_path)
        tables.append((data_path.name, headers, body))
        title = args.title or stem.replace("-", " ").replace("_", " ").title()
        for name in dropped:
            log.observe("column %r is not fully numeric — dropped from "
                        "the figures, kept in the printed table (%s: "
                        "marked, never repaired)" % (name, FLAG))
    elif data_path.suffix.lower() == ".json":
        jtitle, tables, series = read_json_series(data_path)
        title = args.title or jtitle or stem
    else:
        print("report: unsupported data type %s (CSV or JSON)" % data_path.suffix)
        return 2, None
    log.observe("%d table(s), %d chartable series" % (len(tables), len(series)))
    for s in series:
        log.observe("series %r: %d point(s)" % (s["name"], len(s["values"])))
    if not series:
        log.result("no chartable series — a report of tables only; stated, "
                   "not padded")
    log.result("title: %s" % title)

    log.phase("Assembly", "the Markdown report is the primary artifact; "
              "TABVLA draws from the same numbers it prints")
    lines = header_block(title, subject="the data in %s" % data_path.name)
    lines += ["## I. The Data", ""]
    for caption, headers, rows in tables:
        lines += ["**%s**" % caption, "",
                  ptk_table.Table(headers, rows).to_markdown()]
    lines += ["## II. The Figures", ""]
    fig_lines = []
    for i, s in enumerate(series, start=1):
        fig_lines.append((i, s))
        lines += ["Figure %d — %s." % (i, s["name"]), "",
                  "![fig: fig-%d.png]" % i, ""]
    lines += ["## Appendix — Figures and their numbers", "",
              "Every figure above, with the exact numbers it was drawn "
              "from. Check any bar against its number; they are the same "
              "list.", ""]
    for i, s in enumerate(series, start=1):
        lines += ["**Figure %d — %s.** %s" % (i, s["name"],
                                              _pairs(s["labels"], s["values"])),
                  ""]
    lines += ["## Colophon", "",
              "Generated by illuminism report %s on %s from `%s`. "
              "Released under ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ."
              % (__version__, civil_date(), data_path), "",
              "Authorship attributed exclusively to Johnathan 'Qasparr' "
              "Monroe (Greek, -ARR, All Rights Reserved, Without Prejudice).",
              "", "Method of Science. Aim of Religion.", "",
              "Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, "
              "ARR, All Rights Reserved, Without Prejudice. Right of claim "
              "hereby reserved and coined under the authority of the "
              "Living Man.", "", "93 — Live, Love, and let Love, Live.", ""]
    md_path = out_dir / (stem + "-report.md")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    log.observe("Markdown report written: %s" % md_path)

    t = tabula.Tabula(str(md_path))
    for i, s in fig_lines:
        source = s.get("source") or (
            "illuminism report %s — data file %s, series %r (%d rows)"
            % (__version__, data_path.name, s["name"], len(s["values"])))
        fig = t.chart(s.get("kind", "bar"), s["labels"], s["values"],
                      title=s["name"], source=source,
                      out_path=str(out_dir / ("fig-%d.png" % i)))
        fig.caption = s.get("caption") or (
            "%s: %s — drawn from %s."
            % (s["name"], _pairs(s["labels"], s["values"]), data_path.name))
        log.observe("figure %d built (%s, %d points) — source: %s"
                    % (i, s.get("kind", "bar"), len(s["values"]), source))
    try:
        pdf_path = t.build(str(out_dir / (stem + "-report.pdf")))
    except tabula.ProvenanceError as exc:
        log.result("the gate refused: %s — no PDF ships (%s)"
                   % (exc, FLAG))
        print("report: GATE REFUSED — %s" % exc)
        return 1, md_path
    log.result("gate passed (%s); illustrated PDF: %s" % (PASS, pdf_path))
    print("report: %s (+ %s)" % (md_path, pdf_path))
    return 0, md_path

# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
