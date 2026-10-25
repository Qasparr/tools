#!/usr/bin/env python3
# =============================================================================
# "The Markdown is the single source of truth; the PDF is its print."
# — after the house builders
#
# Thelemic date: XXV day of October, Dies Solis, Sol in Scorpio,
# Anno V:xii e.n. (2026 e.v.)
#
# 93.
#
# illuminism/compile.py — compile a Markdown document into the finished
# Teacher's Edition PDF: the header format applied, the Flagpole
# footers resolving — N of M — on every page, and the Table of
# Authorities and Colophon scaffolded where the source does not carry
# them.
#
# By Johnathan 'Qasparr' Monroe (Greek, -ARR, All Rights Reserved,
# Without Prejudice). Released under ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ.
#
# METHOD (Scientific Illuminism): the compiler is a pure presentation
# layer over the house Markdown subset (headings, rules, bullets,
# numbered items, tables, paragraphs with **bold** and *italic*, figure
# lines). It invents no content. What it adds is FORMAT, and every
# addition is scaffolding the directive demands — logged, line by line,
# so the difference between the source and the print is auditable.
#
# MECHANISM: line-oriented parse -> fpdf2 document, in the lineage of
# ptk/scripts/twelve-tongues/build_report_pdf.py (the house builder),
# extended three ways:
#   1. the footer is an FPDF footer() with fpdf2's {nb} page-count
#      alias, so "— N of M —" RESOLVES in the print (the house builder
#      stamps "— N —" after the fact; a Teacher's Edition states M);
#   2. scaffolding — a title page for fragments, a Table of Authorities
#      gathered from the document's own citations, a Colophon with the
#      generation note — each only where the source lacks it;
#   3. the Doctrine logo (templates/doctrine-logo.png) heads the print
#      when the file exists; its absence degrades gracefully and is
#      noted in the log and in any scaffolded colophon — never hidden.
# After rendering, the PDF is re-opened (pypdf, when available) and the
# footer text is verified in the extracted text: the claim "footers
# resolve" is checked, not assumed.
#
# DOCTRINE: scaffolding is marked as scaffolding. A generated Table of
# Authorities lists only what the document actually cites; when a
# document cites nothing, the section prints the dry-well sentence —
# the well is stated dry, never padded.
#
# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
# =============================================================================

"""Compile: Markdown -> Teacher's Edition PDF (fpdf2, house lineage)."""

import re
from pathlib import Path

from . import __version__
from .common import (AUTHORSHIP, CLASSIFICATION, FLAGPOLE, FOOTER_LINE,
                     LOGO_PATH, METHOD_AIM, MOTTO, civil_date)

DJ = "/usr/share/fonts/truetype/dejavu"
NOTO = "/usr/share/fonts/truetype/noto"
FONTS = {
    ("base", ""): f"{DJ}/DejaVuSans.ttf",
    ("base", "B"): f"{DJ}/DejaVuSans-Bold.ttf",
    ("base", "I"): f"{NOTO}/NotoSans-Italic.ttf",
}
FALLBACKS = [
    f"{NOTO}/NotoSansCoptic-Regular.ttf",
    f"{NOTO}/NotoSansEthiopic-ExtraLight.ttf",
]

RICH_RE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*)")
NUM_RE = re.compile(r"^(\d+)[.)]\s+")
FIG_RE = re.compile(r"!\[fig:\s*([^\]]+)\]")
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _footer_text(page, total="{nb}"):
    return FOOTER_LINE.format(page=page, total=total)


def _make_doc():
    """The FPDF document with the resolving Flagpole footer."""
    from fpdf import FPDF

    class _Doc(FPDF):
        # MECHANISM: footer() runs per page at render time; {nb} is
        # fpdf2's total-pages alias, substituted at output — so the M
        # in — N of M — is the true count, not a promise.
        def footer(self):
            self.set_y(-14)
            self.set_font("base", "", 7)
            self.set_text_color(120, 120, 120)
            self.cell(0, 6, _footer_text(self.page_no()), align="C")
            self.set_text_color(0, 0, 0)

    pdf = _Doc(format="Letter", unit="mm")
    pdf.alias_nb_pages("{nb}")
    pdf.set_auto_page_break(True, margin=20)
    pdf.set_margins(14, 16, 14)
    for (fam, style), path in FONTS.items():
        pdf.add_font(fam, style, path)
    fbs = []
    for i, fb in enumerate(FALLBACKS):
        if Path(fb).exists():
            pdf.add_font("fb%d" % i, "", fb)
            fbs.append("fb%d" % i)
    if fbs:
        pdf.set_fallback_fonts(fbs)
    # MECHANISM: text shaping needs uharfbuzz (fpdf2 >= 2.8). It is an
    # optional typography dependency: when it is absent the compiler
    # degrades to unshaped text and says so in the run log — it does
    # not refuse to compile.
    try:
        pdf.set_text_shaping(True)
        pdf.shaping_active = True
    except Exception:
        pdf.shaping_active = False
    return pdf


def _write_rich(pdf, text, size=10):
    """MECHANISM (house pattern): honor **bold** and *italic* inline via
    alternating write() calls; markers are consumed, never printed."""
    from fpdf import XPos, YPos
    pdf.set_font("base", "", size)
    for chunk in RICH_RE.split(text):
        if not chunk:
            continue
        if chunk.startswith("**") and chunk.endswith("**") and len(chunk) > 4:
            pdf.set_font("base", "B", size)
            pdf.write(5.5, chunk[2:-2])
        elif chunk.startswith("*") and chunk.endswith("*") and len(chunk) > 2:
            pdf.set_font("base", "I", size)
            pdf.write(5.5, chunk[1:-1])
        else:
            pdf.set_font("base", "", size)
            pdf.write(5.5, chunk)
    pdf.ln(7)


def _render_table(pdf, rows):
    """MECHANISM (house pattern): pdf.table(), last column double width."""
    if not rows:
        return
    ncols = max(len(r) for r in rows)
    rows = [r + [""] * (ncols - len(r)) for r in rows]
    usable = pdf.w - pdf.l_margin - pdf.r_margin
    unit = usable / (ncols + 1)
    widths = [unit] * (ncols - 1) + [unit * 2]
    pdf.set_font("base", "", 8)
    with pdf.table(col_widths=widths, line_height=5) as table:
        hr = table.row()
        for h in rows[0]:
            hr.cell(h)
        for r in rows[1:]:
            row = table.row()
            for c in r:
                row.cell(c)
    pdf.ln(4)


def _scaffold_authorities(text):
    """Gather the document's own citations into a Table of Authorities.

    MECHANISM: Markdown link targets, in order of first citation,
    de-duplicated. Nothing else is an authority this compiler may name."""
    seen, out = set(), []
    for url in LINK_RE.findall(text):
        if url not in seen:
            seen.add(url)
            out.append(url)
    lines = ["## Table of Authorities", ""]
    if out:
        lines += ["- %s" % u for u in out]
    else:
        lines.append("No authorities are cited in the source document. "
                     "The well is dry, and the dryness is stated, never "
                     "padded.")
    lines.append("")
    return lines


def _scaffold_colophon(source_name, logo_note):
    """The Colophon scaffold: generation note, authorship, Flagpole."""
    lines = ["## Colophon", "",
             "Generated by illuminism compile %s on %s from `%s`. "
             "Released under ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ."
             % (__version__, civil_date(), source_name), ""]
    if logo_note:
        lines += [logo_note, ""]
    lines += [AUTHORSHIP, "", METHOD_AIM + ".", "", FLAGPOLE, "", MOTTO, ""]
    return lines


def run(args, log):
    """illuminism compile — Markdown in, Teacher's Edition PDF out."""
    from fpdf import XPos, YPos

    src = Path(args.document)
    if not src.is_file():
        print("compile: document not found: %s" % src)
        return 2, None
    out = Path(args.out) if args.out else src.with_suffix(".pdf")
    text = src.read_text(encoding="utf-8")
    lines = text.splitlines()

    log.phase("Survey", "the source either carries the Teacher's Edition "
              "format or lacks named pieces of it; the compiler scaffolds "
              "only what is lacking")
    has_h1 = bool(re.search(r"^# ", text, re.M))
    has_flagpole = "Flagpole of Claim and Coinage" in text
    has_authorities = "Table of Authorities" in text
    has_colophon = bool(re.search(r"^#+\s+.*Colophon", text, re.M))
    logo_exists = LOGO_PATH.is_file()
    log.observe("H1 title: %s · Flagpole: %s · Table of Authorities: %s · "
                "Colophon: %s · Doctrine logo on file: %s"
                % (has_h1, has_flagpole, has_authorities, has_colophon,
                   logo_exists))
    if not logo_exists:
        log.observe("no Doctrine logo at %s — compiling without it; the "
                    "absence is noted here and in any scaffolded colophon"
                    % LOGO_PATH)

    extra = []
    if not has_authorities:
        extra += _scaffold_authorities(text)
        log.observe("Table of Authorities scaffolded from the document's "
                    "own citations")
    logo_note = ("" if logo_exists else
                 "Compiled without the Doctrine logo — no file at "
                 "templates/doctrine-logo.png at compile time.")
    if not has_colophon:
        extra += _scaffold_colophon(src.name, logo_note)
        log.observe("Colophon scaffolded (generation note, authorship, "
                    "Flagpole, motto)")

    pdf = _make_doc()
    if not pdf.shaping_active:
        log.observe("text shaping inactive — uharfbuzz is not installed; "
                    "compiling unshaped (typographic degradation, stated, "
                    "not hidden)")
    title = args.title or src.stem.replace("-", " ").replace("_", " ").title()

    # ---- title page for fragments --------------------------------------
    pdf.add_page()
    body_start_page = 1
    if not has_h1:
        log.observe("fragment (no H1): a title page is scaffolded")
        pdf.ln(28)
        if logo_exists:
            w = 38
            pdf.image(str(LOGO_PATH), x=(pdf.w - w) / 2, w=w)
            pdf.ln(8)
        pdf.set_font("base", "B", 22)
        pdf.multi_cell(0, 11, title, align="C",
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)
        pdf.set_font("base", "I", 11)
        pdf.multi_cell(0, 6, "A Scientific Illuminist treatment of %s"
                       % title, align="C", new_x=XPos.LMARGIN,
                       new_y=YPos.NEXT)
        pdf.ln(8)
        for line in (AUTHORSHIP, civil_date() + " — civil date; the "
                     "Thelemic date is penned by hand in house practice.",
                     CLASSIFICATION, METHOD_AIM):
            pdf.set_font("base", "", 10)
            pdf.multi_cell(0, 5.5, line, align="C",
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
        pdf.ln(4)
        pdf.set_font("base", "", 10)
        pdf.multi_cell(0, 5.5, FLAGPOLE, align="C",
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.add_page()
        body_start_page = 2
    elif logo_exists:
        w = 30
        pdf.image(str(LOGO_PATH), x=(pdf.w - w) / 2, w=w)
        pdf.ln(4)

    # ---- body ------------------------------------------------------------
    log.phase("Render", "the house Markdown subset renders line by line; "
              "the footer resolves — N of M — from the true page count")
    para, items, table = [], [], []
    in_table = False

    def flush_para():
        if para:
            _write_rich(pdf, " ".join(para))
            para.clear()

    def flush_items():
        for marker, txt in items:
            pdf.set_font("base", "", 10)
            x = pdf.get_x()
            pdf.set_x(x + 6)
            pdf.write(5.5, marker + " ")
            _write_rich(pdf, txt, size=10)
        items.clear()

    def flush_table():
        if table:
            _render_table(pdf, table)
            table.clear()

    def flush_all():
        flush_para()
        flush_items()
        flush_table()

    for raw in lines + extra:
        line = raw.rstrip()
        s = line.strip()
        if not s:
            flush_para()
            flush_items()
            continue
        if s.startswith("!["):
            flush_all()
            in_table = False
            m = FIG_RE.search(s) or IMG_RE.search(s)
            ref = m.group(1).strip() if m else ""
            img = (src.parent / ref) if ref else None
            if img is not None and img.is_file():
                w = min(150.0, pdf.w - pdf.l_margin - pdf.r_margin)
                if pdf.get_y() + 90 > pdf.h - 24:
                    pdf.add_page()
                pdf.image(str(img), x=pdf.l_margin +
                          (pdf.w - pdf.l_margin - pdf.r_margin - w) / 2, w=w)
                pdf.ln(4)
            else:
                pdf.set_font("base", "I", 9)
                pdf.multi_cell(0, 5.5, "[figure not rendered: %s]" % ref,
                               new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(1)
            continue
        if s.startswith("|"):
            flush_para()
            flush_items()
            in_table = True
            cells = [c.strip() for c in s.strip("|").split("|")]
            if not all(set(c) <= set("-: ") for c in cells):
                table.append(cells)
            continue
        if in_table:
            flush_table()
            in_table = False
        if s.startswith("# "):
            flush_all()
            pdf.set_font("base", "B", 18)
            pdf.multi_cell(0, 9, s[2:], align="C",
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)
        elif s.startswith("## "):
            flush_all()
            if pdf.get_y() > pdf.h - 45:
                pdf.add_page()
            pdf.set_font("base", "B", 13)
            pdf.multi_cell(0, 7, s[3:], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
        elif s.startswith("### "):
            flush_all()
            pdf.set_font("base", "B", 11)
            pdf.multi_cell(0, 6.5, s[4:], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
        elif s == "---":
            flush_all()
            pdf.ln(2)
            pdf.line(pdf.l_margin, pdf.get_y(),
                     pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(4)
        elif s.startswith("- "):
            flush_para()
            items.append(("•", s[2:]))
        elif NUM_RE.match(s):
            flush_para()
            m = NUM_RE.match(s)
            items.append((m.group(1) + ".", s[m.end():]))
        elif s.startswith("*") and s.endswith("*") and len(s) > 2 \
                and not s.startswith("**"):
            flush_all()
            pdf.set_font("base", "I", 9)
            pdf.multi_cell(0, 5.5, s.strip("*"), align="C",
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
        else:
            flush_items()
            para.append(s)
    flush_all()

    out.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out))
    pages = pdf.pages_count
    log.result("PDF written: %s (%d pages, body from page %d)"
               % (out, pages, body_start_page))

    # ---- verification: the footer claim is checked, not assumed ---------
    log.phase("Verification", "the compiled PDF carries the resolving "
              "Flagpole footer in its extracted text")
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(out))
        texts = [(p.extract_text() or "") for p in reader.pages]
        joined = "\n".join(texts)
        found = "Flagpole of Claim and Coinage reserved" in joined
        resolved = bool(re.search(r"—\s*\d+\s*of\s*\d+\s*—", joined))
        literal = "{nb}" in joined
        log.observe("pages: %d · footer text present: %s · — N of M — "
                    "resolved: %s · unresolved alias left: %s"
                    % (len(texts), found, resolved, literal))
        log.result("footer verification: %s"
                   % ("PASS" if (found and resolved and not literal)
                      else "FLAG — see observations"))
    except ImportError:
        log.observe("pypdf is not installed — footer verification stands "
                    "OPEN (the PDF itself was produced; the check was not "
                    "run, and the difference is stated)")
    print("compile: %s (%d pages)" % (out, pages))
    return 0, out

# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
