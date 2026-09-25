#!/usr/bin/env python3
"""Drop the old website's usage instructions from a lesson intro page, in place.

Baker's intro pages (deal00.html, and the partnership review.html) explain how to use the
original website: "decide what you would bid, then click BID. The subsequent page will
then appear...", "use the left Navigation panel", "Click any Deal to start." The intros
are converted to the *_Intro.pdf that Bridge Classroom shows and that starts every
printed handout, where none of that is true. Issue #56.

Sentences that describe the website's pages or navigation are dropped (see USAGE_RE);
everything else is kept, e.g. "you will always be in the South position". A paragraph
left empty goes, and so does a section heading such as ABOUT THE DEALS when nothing is
left under it.

Called by convert_html_to_pdf.sh on its preprocessed copy of each page.
Usage: strip_intro_usage.py FILE [--dry-run]
"""

import html
import re
import sys

# A sentence describing the website's page flow or navigation. Deliberately specific:
# content sentences that merely say "page" ("readers of these pages", "top of the page")
# stay.
USAGE_RE = re.compile(
    r"\bclick"
    r"|\b(?:first|next|subsequent|final|last|this|bidding) (?:few )?pages?\b"
    r"|\bfirst page\b|\bsubsequent pages\b|\beach page\b|\bthe page to look at\b"
    r"|navigation panel|menu ?bar|\bthe link\b"
    r"|partner's hand (?:is also|will be) shown|all four hands (?:will be )?shown"
    r"|next page shows",
    re.IGNORECASE,
)

# Paragraph separator: two <br>s, with any whitespace between.
SEP_RE = re.compile(r"(<br\s*/?>\s*<br\s*/?>)", re.IGNORECASE)

# End of a sentence inside a paragraph's HTML: . ? or ! (tags in these pages never hold
# one), plus any closing ")" or tags, followed by whitespace or a <br>.
SENT_END_RE = re.compile(r"[.?!](?:\)|</\w+>)*(?:\s|<br\s*/?>)+", re.IGNORECASE)

# A paragraph that is only a bold heading, e.g. <b>ABOUT THE DEALS</b>.
HEADING_RE = re.compile(r"^\s*<b>[^<]*</b>\s*$", re.IGNORECASE)


def text_of(fragment):
    t = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(t).replace("\xa0", " ")).strip()


def strip_sentences(para):
    """Drop the usage sentences from one paragraph. Returns (new_para, dropped)."""
    sents, at = [], 0
    for m in SENT_END_RE.finditer(para):
        sents.append(para[at:m.end()])
        at = m.end()
    sents.append(para[at:])
    kept, dropped = [], []
    for sent in sents:
        if USAGE_RE.search(text_of(sent)):
            dropped.append(text_of(sent))
        else:
            kept.append(sent)
    return "".join(kept), dropped


def strip(page):
    """Return (new_page, dropped_sentence_texts)."""
    parts = SEP_RE.split(page)  # [para, sep, para, sep, ...]
    paras, seps = parts[0::2], parts[1::2] + [""]
    dropped, emptied = [], []
    for i, p in enumerate(paras):
        new, d = strip_sentences(p)
        dropped += d
        emptied.append(bool(d) and not text_of(new))
        paras[i] = new
    keep = [not e for e in emptied]
    # A heading whose whole section was emptied goes too.
    for i, p in enumerate(paras):
        if keep[i] and HEADING_RE.match(p):
            j = i + 1
            while j < len(paras) and not keep[j]:
                j += 1
            if j > i + 1 and (j >= len(paras) or HEADING_RE.match(paras[j])):
                keep[i] = False
                dropped.append(f"(heading) {text_of(p)}")
    out = "".join(p + s for p, s, k in zip(paras, seps, keep) if k)
    return out, dropped


def main():
    path, dry = sys.argv[1], "--dry-run" in sys.argv
    with open(path, encoding="utf-8", errors="replace") as f:
        page = f.read()
    new, dropped = strip(page)
    if dry:
        for d in dropped:
            print(f"  - {d[:150]}")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)


if __name__ == "__main__":
    main()
