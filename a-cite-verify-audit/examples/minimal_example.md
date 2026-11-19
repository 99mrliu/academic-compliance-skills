# 最小调用示例（示意输出，非正式案例结果）

## 输入

- `/input/case.json`：`{"case_id": "demo-1", "task": "审查该稿件的引用规范", "output_contract": ["status", "findings"]}`
- `/input/task.md`：题目要求
- `/input/paper.pdf`：稿件 PDF

## 调用

```bash
mkdir -p /app/work /app/output
pdftotext -layout /input/paper.pdf /app/work/paper.txt
python3 /skills/weekly-skill/scripts/extract_refs.py /app/work/paper.txt /app/work/refs.json
python3 /skills/weekly-skill/scripts/extract_citations.py /app/work/paper.txt /app/work/citations.json
python3 /skills/weekly-skill/scripts/lint_refs.py /app/work/refs.json /app/work/lint.json
# 随后按 SKILL.md phase 3-5：模型判读 + 至多 12 次联网核验 + 写 result.json
```

## 示意输出（标注为示例）

`refs.json`（节选）：

```json
{"reference_count": 3, "entries": [
 {"index": 1, "raw": "[1] Wang L, Chen H. Deep learning for genomics. Nat Methods. 2021;18(1):45-52.",
  "page": null, "authors_guess": "Wang L, Chen H", "year": "2021",
  "title_guess": "Deep learning for genomics", "venue_guess": "Nat Methods", "doi": null},
 {"index": 2, "raw": "[2] Zhang Y. Single-cell atlas. Cell. 2024;189:100-130.", "year": "2024", ...}
]}
```

`lint.json`（节选）：

```json
{"candidate_count": 1, "candidates": [
 {"index": null, "issue": "numbering_gap", "detail": "reference indexes: [1, 2, 4]"}]}
```

`result.json`（节选，示例）：

```json
{
  "case_id": "demo-1",
  "status": "complete",
  "findings": [
    {"id": "F1", "type": "metadata_mismatch", "severity": "major",
     "location": {"file": "paper.pdf", "page": 11, "section": "References",
       "quote": "[1] Wang L, Chen H. Deep learning for genomics. Nat Methods. 2021;18(1):45-52."},
     "evidence": "本次检索 PubMed：该文实际刊于 Nat Biotechnol 2021;39(1):45-52",
     "suggestion": "更正期刊名为 Nat Biotechnol；补 DOI 10.1038/s41587-020-xxx",
     "verdict_status": "确认"}
  ],
  "evidence_sources": ["PubMed record (fetched this run)", "local lint rule numbering_gap"],
  "uncertainty": ["条目 [3] 未核验（超出本次检索预算），标记待复核"],
  "not_reviewed": ["页 12 缺失，涉及条目 [4] 的上下文无法核对"],
  "change_log": ["phase0: preflight 完成", "phase4: 执行检索 3 次后达预算上限"]
}
```
