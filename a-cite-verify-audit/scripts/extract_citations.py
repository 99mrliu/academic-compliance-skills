#!/usr/bin/env python3
"""extract_citations.py - locate in-text citation markers with context.

Usage: extract_citations.py <paper.txt> <out.json>

Detects numeric markers ([12], [3, 7-9], [12-14]) and author-year markers
((Wang et al., 2021), Wang et al. (2021), (Wang and Li 2021)). Skips the
reference list section when its heading is found. For each marker it records
the enclosing sentence as a verbatim quote.

Output JSON:
  {"marker_count": N, "markers": [
     {"raw": str, "page": int|null, "style": "numeric"|"authoryear",
      "ref_numbers": [int], "context": str}]}
"""
import json
import re
import sys

REF_HEADINGS = [r"^\s*references\s*$", r"^\s*参考文献\s*$", r"^\s*bibliography\s*$"]

NUM_RE = re.compile(r"\[(\d{1,3}(?:\s*[-,–]\s*\d{1,3})*(?:\s*,\s*\d{1,3}(?:\s*[-,–]\s*\d{1,3})*)*)\]")
AY_RE = re.compile(
    r"(\(?\s*([A-Z][A-Za-z\u00C0-\u024F'`-]+(?:\s+et\s+al\.?|"
    r"(?:\s+and\s+|\s*&\s+)[A-Z][A-Za-z'`-]+)?)\s*\(?,?\s*"
    r"((?:19|20)\d{2}[a-z]?)\s*\)?)")


def expand_numbers(spec):
    nums = set()
    for part in re.split(r"\s*,\s*", spec):
        m = re.match(r"^(\d{1,3})\s*[-–]\s*(\d{1,3})$", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if b - a <= 50:
                nums.update(range(a, b + 1))
        elif part.strip().isdigit():
            nums.add(int(part.strip()))
    return sorted(nums)


def sentence_around(text, start, end, win=240):
    left = max(text.rfind(". ", 0, start), text.rfind("。 ", 0, start))
    right = text.find(". ", end)
    if right == -1:
        right = len(text)
    s = text[left + 1:right + 1].strip()
    if len(s) > 2 * win:
        s = text[max(0, start - win):end + win].strip()
    return s


def main():
    if len(sys.argv) != 3:
        sys.stderr.write("usage: extract_citations.py <paper.txt> <out.json>\n")
        return 2
    src, dst = sys.argv[1], sys.argv[2]
    try:
        text = open(src, encoding="utf-8", errors="replace").read()
    except OSError as e:
        sys.stderr.write("cannot read input: %s\n" % e)
        return 1

    # cut off the reference list to avoid matching entry numbers
    body = text
    cut = None
    for pat in REF_HEADINGS:
        m = re.search(pat, text, re.I | re.M)
        if m:
            cut = m.start()
    if cut is not None:
        body = text[:cut]

    markers = []
    seen = set()
    for m in NUM_RE.finditer(body):
        key = ("n", m.start())
        if key in seen:
            continue
        seen.add(key)
        markers.append({
            "raw": m.group(0),
            "page": None,
            "style": "numeric",
            "ref_numbers": expand_numbers(m.group(1)),
            "context": sentence_around(body, m.start(), m.end()),
        })
    for m in AY_RE.finditer(body):
        yr = m.group(3)[:4]
        if not yr.isdigit() or not (1950 <= int(yr) <= 2100):
            continue
        key = ("a", m.start())
        if key in seen:
            continue
        seen.add(key)
        markers.append({
            "raw": m.group(0),
            "page": None,
            "style": "authoryear",
            "ref_numbers": [],
            "authors_raw": m.group(2),
            "year": m.group(3),
            "context": sentence_around(body, m.start(), m.end()),
        })
    # order: numeric markers first (stable by text order within each style)
    json.dump({"marker_count": len(markers), "markers": markers},
              open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
