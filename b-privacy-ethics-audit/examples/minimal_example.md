# 最小调用示例（示意输出，非正式案例结果）

## 输入

- `/input/case.json`：`{"case_id": "demo-p1", "task": "审查该稿件的隐私与伦理合规", "output_contract": ["status", "findings"]}`
- `/input/paper.pdf`：稿件 PDF

## 调用

```bash
mkdir -p /app/work /app/output
pdftotext -layout /input/paper.pdf /app/work/paper.txt
python3 /skills/weekly-skill/scripts/locate_declarations.py /app/work/paper.txt /app/work/declarations.json
python3 /skills/weekly-skill/scripts/scan_pii.py /app/work/paper.txt /app/work/pii.json
# 随后按 SKILL.md phase 3-4：对照条款库逐条核对 + 写 result.json
```

## 示意输出（标注为示例）

`declarations.json`（节选）：

```json
{"consent": {"present": false, "page": null, "quote": null},
 "ethics": {"present": true, "page": 7,
   "quote": "...The study was approved by the Ethics Committee of XX Hospital (No. 2023-KY-041)...",
   "approval_id_candidate": "2023-KY-041"},
 "data_availability": {"present": false, "page": null, "quote": null}}
```

`pii.json`（节选）：

```json
{"hit_count": 2, "hits": [
 {"rule": "cn_id_number", "page": 5,
  "matched": "110101199001011234",
  "quote": "患者 张某某（身份证 110101199001011234）于 2022 年就诊...", 
  "note": "18 位身份证号样式（含出生日期段）"},
 {"rule": "named_patient_cn", "page": 5, "matched": "患者 张某某", "quote": "...", 
  "note": "患者+姓名组合（中文）"}]}
```

`result.json`（节选，示例）：

```json
{"case_id": "demo-p1", "status": "complete",
 "findings": [
  {"id": "F1", "type": "pii_exposure", "severity": "critical",
   "location": {"file": "paper.pdf", "page": 5, "section": "Table 2",
     "quote": "患者 张某某（身份证 110101199001011234）..."},
   "evidence": "PIPL 第 28 条；HIPAA Safe Harbor 标识符清单（医疗记录/直接标识）；材料 consent 声明缺失（declarations.consent.present=false）",
   "suggestion": "删除身份证号；患者以编号 P05 指代；补知情同意声明，说明同意发表",
   "verdict_status": "确认"},
  {"id": "F2", "type": "consent_missing", "severity": "major",
   "location": {"file": "paper.pdf", "page": 7, "section": "Declarations", "quote": null},
   "evidence": "赫尔辛基宣言（2013）第 25–26 条；脚本扫描全文无 consent 段落",
   "suggestion": "在 Declarations 补：所有参与者签署书面知情同意（含同意发表），或说明豁免依据",
   "verdict_status": "确认"}
 ],
 "uncertainty": ["批件 2023-KY-041 的适用范围无法从材料判断，标记待复核"],
 "not_reviewed": [],
 "change_log": ["phase0: preflight 完成", "phase1: 8 类声明定位完成"]}
```
