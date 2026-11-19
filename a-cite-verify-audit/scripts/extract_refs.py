#!/usr/bin/env python3
"""extract_refs.py - split the reference list out of pdftotext output.

Usage: extract_refs.py <paper.txt> <out.json>

Input: plain text with form feeds (\\f) marking page breaks (pdftotext default).
Output JSON:
  {"reference_count": N, "entries": [
     {"index": int, "raw": str, "page": int|null,
      "authors_guess": str|null, "year": str|null,
      "title_guess": str|null, "venue_guess": str|null, "doi": str|null}]}

Heuristics only; a zero or low count is a signal to re-check the section
heading, not a failure. Exits nonzero on unreadable input.
"""
import json
import re
import sys

REF_HEADINGS = [
    r"^\s*references\s*$", r"^\s*reference\s*$",
    r"^\s*参考文献\s*$", r"^\s*参考书目\s*$",
    r"^\s*bibliography\s*$",
]

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>\)\]]+", re.I)
YEAR_RE = re.compile(r"\b(19|20)\d{2}[a-z]?\b")


def split_pages(text):
    pages = text.split("\f")
    return pages


def find_ref_start(pages):
    """Return (page_idx, line_idx) of the references heading, or None."""
    for pi, page in enumerate(pages):
        lines = page.splitlines()
        for li, line in enumerate(lines):
            s = line.strip()
            for pat in REF_HEADINGS:
                if re.match(pat, s, re.I):
                    # ignore a heading mentioned inline early in the paper
                    if pi < len(pages) // 2 and li < len(lines) - 1:
                        # heading usually near bottom or top of a page; accept anyway
                        pass
                    return pi, li
    return None


ENTRY_START_RES = [
    re.compile(r"^\s*\[(\d{1,3})\]\s*"),
    re.compile(r"^\s*(\d{1,3})[.)]\s+"),
    re.compile(r"^\s*(\d{1,3})\s{2,}"),
]


def looks_like_entry_start(line):
    for r in ENTRY_START_RES:
        if r.match(line):
            return True
    # author-year style: line starts with capitalized surname
    if re.match(r"^\s*[A-Z][A-Za-z'`-]{2,},\s+[A-Z]", line):
        return True
    return False


def split_entries(lines):
    entries, cur = [], []
    for line in lines:
        if not line.strip():
            continue
        if looks_like_entry_start(line) and cur:
            entries.append(" ".join(cur))
            cur = [line.strip()]
        else:
            cur.append(line.strip())
    if cur:
        entries.append(" ".join(cur))
    return entries


def guess_fields(raw):
    doi = DOI_RE.search(raw)
    years = YEAR_RE.findall(raw)
    year = years[0] if years else None
    if year:
        m = YEAR_RE.search(raw)
        year = m.group(0)
    authors = None
    m = re.match(r"^\[?\d*\]?\s*([^.]{3,80}?)\.", raw)
    if m:
        authors = m.group(1).strip()
    # crude title guess: longest sentence-like segment before the year
    title = None
    segs = [s.strip() for s in re.split(r"[.?]\s+", raw) if s.strip()]
    for s in segs:
        if year and year in s:
            continue
        if len(s) > 12 and not re.match(r"^(pp?|vol|Vol|In:|ed)", s):
            title = s[:200]
            break
    venue = None
    m = re.search(r"\.\s*([^.]{4,60}?)\.\s*(?:19|20)\d{2}", raw)
    if m:
        venue = m.group(1).strip()
    else:
        m = re.search(r"(19|20)\d{2}[a-z]?\s*[;,.]\s*([^.]{2,40}?)[,.]", raw)
        if m:
            venue = m.group(2).strip()
    return {
        "authors_guess": authors,
        "year": year,
        "title_guess": title,
        "venue_guess": venue,
        "doi": doi.group(0).rstrip(".,;)") if doi else None,
    }


def main():
    if len(sys.argv) != 3:
        sys.stderr.write("usage: extract_refs.py <paper.txt> <out.json>\n")
        return 2
    src, dst = sys.argv[1], sys.argv[2]
    try:
        with open(src, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:
        sys.stderr.write("cannot read input: %s\n" % e)
        return 1
    pages = split_pages(text)
    start = find_ref_start(pages)
    if start is None:
        json.dump({"reference_count": 0, "entries": [],
                   "warning": "no references heading found"},
                  open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return 0
    pi, li = start
    lines = []
    # skip heading line itself
    for p in pages[pi:]:
        pl = p.splitlines()
        if p is pages[pi]:
            pl = pl[li + 1:]
        lines.extend(pl)
    raw_entries = split_entries(lines)
    out = []
    for i, raw in enumerate(raw_entries, 1):
        fields = guess_fields(raw)
        out.append({"index": i, "raw": raw, "page": None, **fields})
    json.dump({"reference_count": len(out), "entries": out},
              open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
