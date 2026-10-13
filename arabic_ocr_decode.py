#!/usr/bin/env python3
# =============================================================================
# arabic_ocr_decode.py — recover logical-order Arabic from garbled OCR.
#
# Thelemic date: Tue 2026-10-13. 93.
# By Johnathan 'Qasparr' (Κασπάρρ) Monroe, Keeper of the Secret Treasure.
#
# MECHANISM: OCR of Arabic-script print often emits text in VISUAL order
# (left-to-right as printed) using Arabic PRESENTATION FORMS (U+FB50-FDFF,
# U+FE70-FEFF) instead of logical order with standard codepoints. This tool
# reverses each Arabic token and normalizes presentation forms back to
# standard Arabic (U+0600-06FF), so the result can be weighed, searched, or
# read. Latin tokens (e.g. stray "or") and digits are passed through
# untouched; the "*" sigil sometimes prefixed to entries is preserved.
#
# DOCTRINE: decoding is mechanical, not interpretive — the tool never
# guesses vowels, never "corrects" spelling, never reorders words. What the
# OCR gave is what you get, in logical order. Ambiguity stays visible.
#
# USAGE: decode_token("حمﻄﻤﺘک") -> logical-order standard Arabic.
#        decode_line("15 حمﻄﻤﺘک . . .") -> "15 <arabic> . . ."
#
# Live, Love, and let Love, Live. — 93.
# All Rights Reserved, Without Prejudice.
# =============================================================================

import unicodedata
import re

# -- Presentation-form normalization ----------------------------------------
# MECHANISM: NFKC folds nearly all Arabic presentation forms to their
# standard codepoints (isolated/initial/medial/final -> base letter).
# Persian/Urdu extras (ک U+06A9, ی U+06CC, etc.) survive NFKC as-is;
# normalize_persian() optionally folds those to Arabic-script equivalents
# for abjad weighing (flagged, never silent).
def _nfkc(s):
    return unicodedata.normalize('NFKC', s)

PERSIAN_FOLD = {
    'ک': 'ك',  # U+06A9 -> U+0643 Arabic kaf
    'ی': 'ي',  # U+06CC -> U+064A Arabic ya
    'ھ': 'ه',  # U+06BE -> U+0647 Arabic heh
    'ۃ': 'ة',  # U+06C3 -> teeh marbuta goal
    'گ': 'ك',  # U+06AF gaf -> kaf (nearest abjad equivalent; FLAGGED)
    'پ': 'ب',  # U+06A4 peh -> beh (nearest; FLAGGED)
    'چ': 'ج',  # U+0686 tcheh -> jeem (nearest; FLAGGED)
    'ژ': 'ز',  # U+0698 jeh -> zain (nearest; FLAGGED)
    'ؤ': 'ؤ',  # already standard
}

def normalize_persian(s):
    """Fold Persian/Urdu letter variants to Arabic-script equivalents.
    DOCTRINE: only for weighing; the unfolded form stays on record."""
    return ''.join(PERSIAN_FOLD.get(ch, ch) for ch in s)

_ARABIC_RE = re.compile(r'[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]+')

def decode_token(tok):
    """MECHANISM: one visual-order Arabic token -> logical-order standard.
    Reverse the character sequence (visual LTR -> logical RTL), then NFKC.
    Non-Arabic tokens returned unchanged."""
    if not _ARABIC_RE.search(tok):
        return tok
    return _nfkc(tok[::-1])

def decode_line(line):
    """Decode every Arabic token in a mixed line, preserving order/others."""
    return _ARABIC_RE.sub(lambda m: _nfkc(m.group(0)[::-1]), line)

def is_arabic_word(tok):
    return bool(_ARABIC_RE.fullmatch(tok))

# -- Arabic -> Hebrew consonantal transliteration -----------------------------
# MECHANISM: the Celephais endnote to 777's Col. XLVII observes the names
# can be "transliterated into Hebrew". Straight consonant mapping, Eastern
# abjad order assumed. DOCTRINE: transliteration is DERIVED tier — a bridge
# check, never a second attestation of the same weighing.
AR2HE = {
    'ا': 'א', 'ب': 'ב', 'ج': 'ג', 'د': 'ד', 'ه': 'ה', 'ة': 'ה',
    'و': 'ו', 'ز': 'ז', 'ح': 'ח', 'ط': 'ט', 'ي': 'י', 'ى': 'י',
    'ك': 'כ', 'ک': 'כ', 'ل': 'ל', 'م': 'מ', 'ن': 'נ', 'س': 'ס',
    'ع': 'ע', 'ف': 'פ', 'ص': 'צ', 'ق': 'ק', 'ر': 'ר', 'ش': 'ש',
    'ت': 'ת', 'ث': 'ת', 'خ': 'ח', 'ذ': 'ד', 'ض': 'צ', 'ظ': 'ט',
    'غ': 'ע', 'ء': 'א', 'ؤ': 'ו', 'ئ': 'י', 'أ': 'א', 'إ': 'א', 'آ': 'א',
}

def transliterate_hebrew(arabic_word):
    """Arabic-script word -> Hebrew-script consonantal transliteration.
    Characters with no mapping are kept as-is (visible, not dropped)."""
    return ''.join(AR2HE.get(ch, ch) for ch in arabic_word)

if __name__ == '__main__':
    # Self-test on the worker-02 row-15 cell (visual-order OCR).
    got = decode_token("حمﻄﻤﺘک")
    print("row15 decoded:", got)
    print("row15 persian-folded:", normalize_persian(got))
    print("row15 hebrew:", transliterate_hebrew(normalize_persian(got)))
