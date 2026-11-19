#!/usr/bin/env python3
"""lint_refs.py - local consistency screening of a parsed reference list.

Usage: lint_refs.py <refs.json> <out.json>

Checks (heuristic, stdlib-only):
  duplicate_of      near-identical normalized titles / DOIs
  missing_year      no year found
  future_year       year later than current year
  missing_venue     no journal/conference-like segment detected
  doi_malformed     DOI-like string failing the 10.xxxx/ prefix pattern
  numbering_gap     numeric indexes not consecutive
  style_mix_hint    entries mixing numbered and unnumbered styles

Candidates only - the agent decides what becomes a finding.
"""
import json
import re
import sys
from datetime import date

STOP = set("the a an of and in on for to with by from at as is are was were "
           "de la le et al eds ed vol pp press journal proceedings".split())


def norm_title(t):
    if not t:
        return ""
    words = re.findall(r"[a-z0-9]+", t.lower())
    return " ".join(w for w in words if w not in STOP)


def token_overlap(a, b):
    sa, sb = set(norm_title(a).split()), set(norm_title(b).split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def main():
    if len(sys.argv) != 3:
        sys.stderr.write("usage: lint_refs.py <refs.json> <out.json>\n")
        return 2
    try:
        data = json.load(open(sys.argv[1], encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write("cannot read refs.json: %s\n" % e)
        return 1
    entries = data.get("entries", [])
    cands = []
    cur_year = date.today().year

    for e in entries:
        idx, raw = e.get("index"), e.get("raw", "")
        year = e.get("year")
        if not year:
            cands.append({"index": idx, "issue": "missing_year",
                          "detail": "no 19xx/20xx year token in entry"})
        elif int(re.match(r"(19|20)\d{2}", year).group(0)) > cur_year:
            cands.append({"index": idx, "issue": "future_year",
                          "detail": "year %s is in the future" % year})
        if not e.get("venue_guess"):
            cands.append({"index": idx, "issue": "missing_venue",
                          "detail": "no venue-like segment detected (heuristic)"})
        doi = e.get("doi")
        if doi and not re.match(r"^10\.\d{4,9}/\S+$", doi):
            cands.append({"index": idx, "issue": "doi_malformed",
                          "detail": "doi: %s" % doi})
        m = re.search(r"10[\.\s]*\d{3,4}[\.\s]\S+", raw)
        if m and not doi:
            cands.append({"index": idx, "issue": "doi_malformed",
                          "detail": "suspicious doi-like string: %s" % m.group(0)})

    # duplicates by DOI or title overlap
    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            a, b = entries[i], entries[j]
            if a.get("doi") and b.get("doi") and a["doi"] == b["doi"]:
                cands.append({"index": a["index"], "issue": "duplicate_of",
                              "other_index": b["index"], "detail": "same DOI"})
                continue
            ov = token_overlap(a.get("title_guess"), b.get("title_guess"))
            if ov >= 0.8 and norm_title(a.get("title_guess")):
                cands.append({"index": a["index"], "issue": "duplicate_of",
                              "other_index": b["index"],
                              "detail": "title token overlap %.2f" % ov})

    # numbering gaps for numbered lists
    nums = [e["index"] for e in entries if isinstance(e.get("index"), int)]
    if nums and nums == list(range(1, len(nums) + 1)):
        pass  # consecutive
    elif nums:
        cands.append({"index": None, "issue": "numbering_gap",
                      "detail": "reference indexes: %s" % nums[:20]})

    # style mixing: some entries numbered, some not
    numbered = sum(1 for e in entries if re.match(r"^\[?\d+\]?", e.get("raw", "").strip()))
    if entries and 0 < numbered < len(entries):
        cands.append({"index": None, "issue": "style_mix_hint",
                      "detail": "%d/%d entries appear numbered"
                                % (numbered, len(entries))})

    json.dump({"candidate_count": len(cands), "candidates": cands},
              open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
