# 最小调用示例（示意输出，非正式案例结果）

## 输入

- `/input/case.json`：`{"case_id": "demo-v1", "task": "按目标期刊作者指南核对稿件", "venue": null, "output_contract": ["status", "findings"]}`（venue 为空 → 退化到通用核心清单）
- `/input/paper.pdf`：稿件 PDF

## 调用

```bash
mkdir -p /app/work /app/output
pdftotext -layout /input/paper.pdf /app/work/paper.txt
python3 /skills/weekly-skill/scripts/manifest_stats.py /app/work/paper.txt /app/work/stats.json
python3 /skills/weekly-skill/scripts/declaration_inventory.py /app/work/paper.txt /app/work/decl.json
# 随后按 SKILL.md phase 3-5：拆条（此处为通用核心清单）+ 逐条映射 + 写 result.json
```

## 示意输出（标注为示例）

`stats.json`（节选）：

```json
{"sections_detected": [{"name": "abstract", ...}, {"name": "introduction", ...}],
 "abstract_words": 268, "body_words_excl_refs": 5210,
 "figures_referenced": 6, "tables_referenced": 2,
 "keyword_count": 5, "reference_entries_estimate": 32, "pages": 14}
```

`result.json`（节选，示例）：

```json
{"case_id": "demo-v1", "status": "complete",
 "guideline_basis": "generic core checklist (checklist_core.md), no venue specified; retrieval not attempted",
 "checklist_results": [
   {"item": "S1", "result": "pass", "evidence": "abstract section detected"},
   {"item": "D2", "result": "missing", "evidence": "decl.coi.present=false"},
   {"item": "S5", "result": "待复核", "evidence": "abstract_words=268；无目标期刊阈值"}],
 "findings": [
   {"id": "F1", "type": "missing_item", "severity": "major",
    "location": {"file": "paper.pdf", "page": 13, "section": "Declarations", "quote": null},
    "evidence": "通用核心清单 D2（COI 声明）；decl.coi.present=false",
    "suggestion": "补充 Conflict of Interest 声明（无则写 'The authors declare no competing interests.'）",
    "verdict_status": "确认"}],
 "uncertainty": ["摘要字数统计口径为 latin 词+CJK 单字；未含图注"],
 "not_reviewed": [],
 "change_log": ["phase0: preflight 完成", "phase3: venue 缺失，退化到通用核心清单"]}
```
