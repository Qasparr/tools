#!/usr/bin/env python3
# =============================================================================
# "Let the log be the witness." — the scribe
#
# Thelemic date: XXV day of October, Dies Solis, Sol in Scorpio,
# Anno V:xii e.n. (2026 e.v.)
#
# 93.
#
# illuminism/common.py — the shared machinery of the three verbs:
# the standing texts of the Teacher's Edition format, discovery of the
# Architect's toolkits, and the ultra-verbose run log.
#
# By Johnathan 'Qasparr' Monroe (Greek, -ARR, All Rights Reserved,
# Without Prejudice). Released under ΕΠΙΣΤΗΜΟΝΙΚΟΣ ΙΛΛΟΥΜΙΝΙΣΜΟΣ.
#
# METHOD (Scientific Illuminism): hypothesis -> method -> observation ->
# result. The RunLog below is that method as a data structure: every run
# of every verb records its phases in the four beats, so the log of a run
# can be audited the way the run audits its target.
#
# MECHANISM: three toolkits are found, never vendored — ptk (PONTIFEX),
# tabula (TABVLA), vestigator (VESTIGATOR). Discovery order: environment
# variable, then the settled workspace home. sys.path is extended at load
# time, per verb, so a verb imports only the instruments it actually uses.
#
# DOCTRINE: the standing texts (authorship, classification, Flagpole) are
# quoted from ~/workspace/templates/teachers-edition-header.md — the
# header directive itself — so this package and the template can never
# drift apart silently; if the template changes, change these constants
# in the same commit and say so.
#
# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
# =============================================================================

"""Shared machinery: standing texts, tool discovery, the run log."""

import os
import sys
import time
from pathlib import Path

from . import GREEK_TITLE, RELEASE_LINE, __version__

# ---------------------------------------------------------------------------
# The standing texts of the Teacher's Edition format.
# DOCTRINE: quoted from templates/teachers-edition-header.md (the system
# directive, 2026-10-25). The words are the Architect's; the scribe copies.
# ---------------------------------------------------------------------------

AUTHORSHIP = ("Authorship attributed exclusively to Johnathan 'Qasparr' "
              "Monroe (Greek, -ARR, All Rights Reserved, Without Prejudice)")

CLASSIFICATION = "Classification: Enterprise • Educational • Research & Development"

METHOD_AIM = "Method of Science, Aim of Religion"

FLAGPOLE = ("Flagpole of Claim and Coinage: Johnathan 'Qasparr' Monroe, ARR, "
            "All Rights Reserved, Without Prejudice. Right of claim hereby "
            "reserved and coined under the authority of the Living Man.")

FOOTER_LINE = ("— {page} of {total} — | All Rights Reserved, Without "
               "Prejudice | Flagpole of Claim and Coinage reserved")

MOTTO = "93 — Live, Love, and let Love, Live."

TEMPLATE_PATH = Path.home() / "workspace" / "templates" / "teachers-edition-header.md"
LOGO_PATH = Path.home() / "workspace" / "templates" / "doctrine-logo.png"

# ---------------------------------------------------------------------------
# Tool discovery.
# MECHANISM: each toolkit has a settled home (ptk lives in the pontifex
# repo's tools/, by the Architect's rule that repo-exclusive tools live in
# that repo; TABVLA and VESTIGATOR are standalone repos). An environment
# variable overrides the home; the default is the workspace layout.
# ---------------------------------------------------------------------------

_TOOL_HOMES = {
    "ptk": ("ILLUMINISM_PTK_HOME", Path.home() / "workspace" / "pontifex" / "tools"),
    "tabula": ("ILLUMINISM_TABULA_HOME", Path.home() / "workspace" / "tabula"),
    "vestigator": ("ILLUMINISM_VESTIGATOR_HOME", Path.home() / "workspace" / "vestigator"),
}


def tool_home(name):
    """Return the home directory of one of the Architect's toolkits.

    DOCTRINE: fail loudly, never guess. If the home is missing, the error
    names the environment variable that would have overridden it."""
    env_var, default = _TOOL_HOMES[name]
    home = Path(os.environ.get(env_var, str(default))).expanduser()
    if not home.is_dir():
        raise FileNotFoundError(
            "%s toolkit not found at %s — set %s to its home" % (name, home, env_var))
    return home


def _load(name):
    """MECHANISM: put the toolkit's home on sys.path (once), import it."""
    home = str(tool_home(name))
    if home not in sys.path:
        sys.path.insert(0, home)
    import importlib
    return importlib.import_module(name)


def load_ptk():
    """The PONTIFEX toolkit (weigh, cipher, table, chart)."""
    return _load("ptk")


def load_tabula():
    """TABVLA (Tabula, gate, ProvenanceError, load_report)."""
    return _load("tabula")


def load_scriba():
    """SCRIBA, VESTIGATOR's case file (vestigator.scriba.CaseFile)."""
    _load("vestigator")
    import importlib
    return importlib.import_module("vestigator.scriba")


def civil_date():
    """MECHANISM: the civil date of the run, e.g. '25 October 2026'.

    DOCTRINE: this package computes no ephemeris. Where a document needs
    a Thelemic date, the document carries its own, penned by hand in
    house practice; generated scaffolding uses the civil date and says so."""
    return time.strftime("%d %B %Y")


def header_block(title, subject=None, date_line=None):
    """Render the Teacher's Edition header block as Markdown lines.

    MECHANISM: title, subtitle, authorship, date, classification,
    Method/Aim, Flagpole — in the template's order, nothing invented.
    `subject` fills the subtitle's 'treatment of …'; `date_line` defaults
    to the civil date with its stated limitation."""
    lines = ["# " + title, ""]
    if subject:
        lines += ["*A Scientific Illuminist treatment of %s*" % subject, ""]
    lines += [AUTHORSHIP, ""]
    lines.append(date_line or ("%s — civil date; the Thelemic date is penned "
                               "by hand in house practice." % civil_date()))
    lines += ["", CLASSIFICATION, "", METHOD_AIM, "", FLAGPOLE, ""]
    return lines


# ---------------------------------------------------------------------------
# The run log.
# ---------------------------------------------------------------------------

class RunLog:
    """The ultra-verbose log of one run, in the four beats.

    MECHANISM: phases are opened with a hypothesis, filled with method /
    observation / result entries, and written as Markdown beside the
    run's outputs. The log is a research record (the Architect's standing
    order): dead ends are observations too, and are never edited out.
    """

    def __init__(self, verb, argv):
        self.verb = verb
        self.argv = list(argv)
        self.started = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._phases = []          # [(title, [(beat, text), ...]), ...]
        self._current = None

    def phase(self, title, hypothesis):
        """Open a phase: title + the hypothesis the phase tests."""
        self._current = (title, [("Hypothesis", hypothesis)])
        self._phases.append(self._current)

    def _beat(self, beat, text):
        if self._current is None:
            self.phase("Prelude", "the run begins")
        self._current[1].append((beat, str(text)))

    def method(self, text):
        self._beat("Method", text)

    def observe(self, text):
        self._beat("Observation", text)

    def result(self, text):
        self._beat("Result", text)

    def note(self, text):
        """A free-standing note (dead end, limitation, aside)."""
        self._beat("Note", text)

    def write(self, path):
        """Render the log as Markdown and write it. Returns the path."""
        out = ["# Run log — illuminism %s" % self.verb, "",
               "%s — %s, version %s. Run at %s." % (GREEK_TITLE, "illuminism",
                                                    __version__, self.started),
               "Command: `illuminism %s`" % " ".join(self.argv), ""]
        for i, (title, beats) in enumerate(self._phases, start=1):
            out += ["## Phase %d — %s" % (i, title), ""]
            for beat, text in beats:
                out.append("**%s:** %s" % (beat, text))
                out.append("")
        out += ["---", "", RELEASE_LINE + ". " + MOTTO, ""]
        Path(path).write_text("\n".join(out), encoding="utf-8")
        return str(path)


# Verdict vocabulary, shared by every ledger the package prints.
# DOCTRINE: PASS = verified against the source; FLAG = a discrepancy or a
# missing demanded element, printed and never buried; OPEN = not decidable
# by this instrument (the reason is always stated). Nothing is deleted,
# nothing is auto-fixed — findings are marked (the Architect's rule).
PASS, FLAG, OPEN = "PASS", "FLAG", "OPEN"

# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
