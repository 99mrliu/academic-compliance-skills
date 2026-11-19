#!/usr/bin/env python3
"""locate_declarations.py - locate standard declaration sections.

Usage: locate_declarations.py <paper.txt> <out.json>

For each declaration type, report present/absent and a verbatim quote.

Declaration keys:
  consent, ethics, data_availability, coi, funding,
  animal_welfare, author_contributions, ai_use
"""
import json
import re
import sys

PATTERNS = {
    "consent": [
        r"informed consent", r"知情同意", r"consent to publish",
        r"consent for publication", r"同意书",
    ],
    "ethics": [
        r"ethic(s|al) (approval|committee|review|board)", r"IRB",
        r"institutional review board", r"伦理(审查|审批|批件|委员会)",
        r"ethik", r"伦理学",
    ],
    "data_availability": [
        r"data (availability|sharing)", r"availability of data",
        r"数据可用性", r"数据共享", r"data access statement",
    ],
    "coi": [
        r"conflict(s)? of interest", r"competing interests?",
        r"利益冲突", r"利益冲突声明",
    ],
    "funding": [
        r"fund(ing|ed)", r"grant(s)? (no\.?|number)", r"基金(资助|项目)",
        r"国家自然科学基金", r"financial support",
    ],
    "animal_welfare": [
        r"animal (ethics|welfare|care|experiment)",
        r"动物(伦理|实验|福利)", r"IACUC", r"ARRIVE",
    ],
    "author_contributions": [
        r"author contributions?", r"作者贡献", r"CRediT",
    ],
    "ai_use": [
        r"(use of |generative )?AI[- ]assist", r"artificial intelligence tool",
        r"大语言模型", r"LLM", r"ChatGPT", r"生成式",
    ],
}

ETHICS_NO_RE = re.compile(
    r"(?:批准|批件|编号|approval|protocol|registration)?\s*(?:no\.?|number|号)?\s*[:：#]?\s*([A-Za-z0-9]{2,}[-/][A-Za-z0-9][-A-Za-z0-9/.]{3,25})")


def page_of(text, pos):
    return text.count("\f", 0, pos) + 1


def main():
    if len(sys.argv) != 3:
        sys.stderr.write("usage: locate_declarations.py <paper.txt> <out.json>\n")
        return 2
    try:
        text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    except OSError as e:
        sys.stderr.write("cannot read input: %s\n" % e)
        return 1
    out = {}
    for key, pats in PATTERNS.items():
        found = None
        for pat in pats:
            m = re.search(pat, text, re.I)
            if m:
                s = max(0, m.start() - 200)
                e = min(len(text), m.end() + 400)
                found = {
                    "present": True,
                    "page": page_of(text, m.start()),
                    "matched_pattern": pat,
                    "quote": text[s:e].replace("\n", " ").strip(),
                }
                break
        out[key] = found or {"present": False, "page": None, "quote": None}

    # try to surface an ethics approval number near the ethics quote
    eq = out.get("ethics", {}).get("quote")
    if eq:
        m = ETHICS_NO_RE.search(eq)
        out["ethics"]["approval_id_candidate"] = m.group(1) if m else None
    json.dump(out, open(sys.argv[2], "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
