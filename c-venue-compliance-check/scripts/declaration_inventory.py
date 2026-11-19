#!/usr/bin/env python3
"""declaration_inventory.py - inventory of standard manuscript declarations.

Usage: declaration_inventory.py <paper.txt> <out.json>

Keys: funding, coi, data_availability, author_contributions, ethics,
consent, animal_welfare, ai_use. Each entry: present/page/quote.
Also reports anonymization signals (author-name-like header lines).
"""
import json
import re
import sys

PATTERNS = {
    "funding": [r"fund(ing|ed)", r"grant(s)?\s+(no\.?|number)",
                r"基金(资助|项目)", r"financial support", r"国家自然科学基金"],
    "coi": [r"conflict(s)? of interest", r"competing interests?", r"利益冲突"],
    "data_availability": [r"data (availability|sharing)",
                          r"availability of data", r"数据可用性", r"数据共享"],
    "author_contributions": [r"author contributions?", r"作者贡献", r"CRediT"],
    "ethics": [r"ethic(s|al) (approval|committee|review|board)",
               r"institutional review board", r"伦理(审查|审批|批件|委员会)"],
    "consent": [r"informed consent", r"知情同意", r"consent (to|for) publish"],
    "animal_welfare": [r"animal (ethics|welfare|care|experiment)",
                       r"动物(伦理|实验|福利)", r"IACUC", r"ARRIVE"],
    "ai_use": [r"generative AI", r"AI[- ]assist", r"large language model",
               r"大语言模型", r"ChatGPT", r"生成式"],
}

AFFIL_HINT = re.compile(r"(university|universit|institute|hospital|academy|"
                        r"college|laborator|大学|学院|研究所|医院|实验室)", re.I)


def page_of(text, pos):
    return text.count("\f", 0, pos) + 1


def main():
    if len(sys.argv) != 3:
        sys.stderr.write("usage: declaration_inventory.py <paper.txt> <out.json>\n")
        return 2
    try:
        text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    except OSError as e:
        sys.stderr.write("cannot read input: %s\n" % e)
        return 1
    out = {"declarations": {}}
    for key, pats in PATTERNS.items():
        found = None
        for pat in pats:
            m = re.search(pat, text, re.I)
            if m:
                s = max(0, m.start() - 150)
                e = min(len(text), m.end() + 350)
                found = {"present": True, "page": page_of(text, m.start()),
                         "matched_pattern": pat,
                         "quote": text[s:e].replace("\n", " ").strip()}
                break
        out["declarations"][key] = found or {"present": False, "page": None,
                                             "quote": None}

    # anonymization signals: affiliation-like lines in the first two pages
    head = "\f".join(text.split("\f")[:2])
    affil_hits = [m.group(0) for m in AFFIL_HINT.finditer(head)]
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", head)
    out["anonymization_signals"] = {
        "affiliation_keywords_in_front_matter": len(affil_hits),
        "emails_in_front_matter": emails[:10],
        "note": "if venue requires double-blind review, these are violations",
    }
    json.dump(out, open(sys.argv[2], "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
