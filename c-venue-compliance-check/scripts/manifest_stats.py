#!/usr/bin/env python3
"""manifest_stats.py - structural and numeric statistics of a manuscript.

Usage: manifest_stats.py <paper.txt> <out.json>

Counts are heuristic and documented as such; the audit must state the counting
convention in `uncertainty` when thresholds are compared.
"""
import json
import re
import sys

SECTION_PATTERNS = {
    "abstract": r"^\s*(abstract|摘要)\s*$",
    "keywords": r"^\s*(key\s*words?|关键词)\s*[:：]?",
    "introduction": r"^\s*\d*\.?\s*(introduction|引言)\s*$",
    "methods": r"^\s*\d*\.?\s*((materials?\s+and\s+)?methods?|方法|材料与方法)\s*$",
    "results": r"^\s*\d*\.?\s*(results?|结果)\s*$",
    "discussion": r"^\s*\d*\.?\s*(discussion|讨论)\s*$",
    "conclusion": r"^\s*\d*\.?\s*(conclusions?|结论)\s*$",
    "references": r"^\s*(references|参考文献|bibliography)\s*$",
    "acknowledgements": r"^\s*(acknowledg(e)?ments?|致谢)\s*$",
}

FIG_RE = re.compile(r"\b(Fig\.?|Figure|图)\s*\d+", re.I)
TAB_RE = re.compile(r"\b(Table|表)\s*\d+", re.I)
EQ_RE = re.compile(r"\b(Eq\.?|Equation|式|公式)\s*\(?\d+", re.I)
KW_RE = re.compile(r"^\s*(key\s*words?|关键词)\s*[:：]\s*(.+)$", re.I | re.M)
REF_ENTRY_RE = re.compile(r"^\s*(?:\[\d{1,3}\]|\d{1,3}[.)]\s)")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def words(text):
    # latin tokens + CJK characters counted individually
    latin = re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", text)
    cjk = re.findall(r"[一-鿿]", text)
    return len(latin) + len(cjk)


def main():
    if len(sys.argv) != 3:
        sys.stderr.write("usage: manifest_stats.py <paper.txt> <out.json>\n")
        return 2
    try:
        text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    except OSError as e:
        sys.stderr.write("cannot read input: %s\n" % e)
        return 1

    lines = text.splitlines()
    sections = []
    sec_positions = {}
    for i, line in enumerate(lines):
        s = line.strip()
        for name, pat in SECTION_PATTERNS.items():
            if re.match(pat, s, re.I):
                sections.append({"name": name, "line": i, "heading": s})
                if name not in sec_positions:
                    sec_positions[name] = i
                break

    # word counts between detected top-level section headings
    section_words = {}
    ordered = sorted({p["line"]: p["name"] for p in sections}.items())
    for k, (ln, name) in enumerate(ordered):
        end = ordered[k + 1][0] if k + 1 < len(ordered) else len(lines)
        section_words[name] = words("\n".join(lines[ln:end]))

    # abstract text: from abstract heading to next section heading
    abstract_words = None
    if "abstract" in sec_positions:
        a = sec_positions["abstract"]
        nxt = min([ln for ln, n in ordered if ln > a] or [len(lines)])
        abstract_words = words("\n".join(lines[a:nxt]))

    # body words (exclude reference list)
    body_end = sec_positions.get("references", len(lines))
    body_words = words("\n".join(lines[:body_end]))

    figs = sorted(set(m.group(0) for m in FIG_RE.finditer(text)))
    tabs = sorted(set(m.group(0) for m in TAB_RE.finditer(text)))
    eqs = sorted(set(m.group(0) for m in EQ_RE.finditer(text)))

    kw = KW_RE.search(text)
    kw_list = []
    if kw:
        kw_list = [k.strip() for k in re.split(r"[,;，；]", kw.group(2)) if k.strip()]

    ref_count = 0
    if "references" in sec_positions:
        for line in lines[sec_positions["references"]:]:
            if REF_ENTRY_RE.match(line):
                ref_count += 1

    emails = EMAIL_RE.findall(text)
    out = {
        "sections_detected": sections,
        "section_words": section_words,
        "abstract_words": abstract_words,
        "body_words_excl_refs": body_words,
        "total_words": words(text),
        "figures_referenced": len(figs), "figure_labels": figs[:50],
        "tables_referenced": len(tabs), "table_labels": tabs[:50],
        "equations_referenced": len(eqs),
        "keywords": kw_list, "keyword_count": len(kw_list),
        "reference_entries_estimate": ref_count,
        "email_count": len(emails),
        "pages": text.count("\f") + 1,
        "counting_convention":
            "words = latin tokens + individual CJK chars; figures/tables "
            "counted as distinct in-text labels, not actual floats",
    }
    json.dump(out, open(sys.argv[2], "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
