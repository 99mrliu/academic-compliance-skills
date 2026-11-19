---
name: venue-compliance-check
description: >-
  投稿要求逐条核对 (venue submission-requirements checklist audit)。当且仅当把
  目标期刊/会议的作者指南拆成可核对条目并逐条映射到稿件时使用本技能：统计稿件
  结构（章节、摘要字数、图表数、参考文献数）、声明完整性（基金、利益冲突、数据
  可用性、作者贡献、伦理、AI 使用）、匿名化（双盲投稿）、图表来源与许可标注，
  报告缺失项、超限项与格式冲突，并注明所依据指南的版本与日期。流程固定为五个
  相位：preflight 锁定输入与初始 result.json；extract 解析稿件结构与文本；
  measure 用脚本统计结构、字数、图表、声明清单；map 将指南条目（或通用核心
  清单）逐条映射判定；compose 产出 findings（原文定位+指南条目+严重度+修改
  建议）写入 /app/output/result.json。不审查引用真实性、隐私或语言质量。Use
  when: mapping a target venue's author guidelines onto a manuscript and
  reporting missing, over-limit, or conflicting items with guideline versions.
---

# 投稿要求逐条核对 venue-compliance-check

## 用途与适用条件

回答三个可核对的问题：

1. 稿件相对目标期刊/会议要求**缺了什么**（必备声明、结构章节、摘要、关键词、亮点/贡献声明等）；
2. 稿件**哪里超限或冲突**（摘要字数、总字数、图表数、参考文献数、双盲匿名性、页数）；
3. 第三方材料（图、表、代码、数据集）的**来源标注与许可**是否清楚。

适用条件（全部满足才启用）：

- 平台提供 `/input/case.json` 与 `/input/task.md`，源材料在 `/input` 下；
- 工作目录 `/app/work`，交付目录 `/app/output`；
- 任务属于投稿合规/期刊指南核对类。

**目标期刊/会议缺失时的退化策略**（重要）：不得编造指南条款。转而使用
`references/checklist_core.md` 的通用核心清单（仅收录多数出版商共通的、可
客观判定的项目），并在 result.json 的 `guideline_basis` 中注明
`"generic core checklist, no venue specified"`；凡需要具体数值阈值的项目
（字数上限、图表上限）一律标 `待复核`，说明"缺少目标期刊阈值"。

不在本技能范围：引用真实性、隐私伦理、语言润色。若 `case.json` 指定其他审查面，仍执行本技能的投稿合规核对并在 `scope_note` 如实说明。

## 依赖

- **仅 Python 3 标准库**（3.8+）。
- `pdftotext`：可选。缺失时用 `/input` 已有文本；皆无则 `status: "blocked"`。
- 联网：可选，仅在 case 材料给出目标期刊名称而材料中未附指南时，用于检索该期刊作者指南（最多 3 次检索；检索不到即退化到通用核心清单，不编造条款）。

## 运行相位

### phase 0 preflight

读取 `/input/case.json`（`case_id`、任务描述、`output_contract`、目标期刊/会议字段）；列出材料；`pdftotext -layout` 抽取文本；立即写初始 `/app/output/result.json`（`status: "partial"`）。

### phase 1-2 extract & measure（脚本确定性统计）

```bash
python3 <skill>/scripts/manifest_stats.py /app/work/paper.txt /app/work/stats.json
python3 <skill>/scripts/declaration_inventory.py /app/work/paper.txt /app/work/decl.json
```

`stats.json`：识别出的章节标题序列、各章词数、摘要词数、图/表/公式引用计数、参考文献条目计数估计、是否存在作者姓名块（匿名化信号）、关键词数。
`decl.json`：八类声明（funding、COI、data availability、author contributions、ethics、consent、animal welfare、AI use）的存在性与逐字摘录。

### phase 3 获取指南条目

优先级：case 材料附带的指南文本 > 材料中指定的指南文件名 > 联网检索（注明版本/日期）> 通用核心清单。把指南拆成**可核对条目**：每条含 `id`、`requirement`、`threshold`（若有）、`source`（指南段落摘录或条目名）。禁止凭印象补充阈值。

### phase 4 map（逐条映射判定）

对每条指南/清单条目，用 stats.json、decl.json 与原文给出判定：`pass` / `violation` / `missing` / `待复核` / `不适用`。判定必须绑定证据：

- 数值类（字数、图表数）：引用脚本统计值 + 指南阈值；
- 存在类（声明、章节）：引用脚本 inventory 或逐字摘录；
- 匿名化：统计作者姓名/单位/致谢/基金信息在正文中出现的位置；双盲要求下出现 → `violation`；
- 许可类：每张非自绘图表应有来源/许可标注（"reproduced from/adapted from/permission"）；缺失 → `missing`。

### phase 5 compose（结构化交付）

每条 finding 含：`id`、`type`（`missing_item` / `over_limit` / `format_conflict` / `licensing_gap` / `anonymization_breach` / `declaration_incomplete` / `suggestion`）、`severity`（critical/major/minor/info，见 `references/severity_rubric.md`）、`location`（文件+页码+章节+逐字摘录）、`evidence`（指南条目 id + 指南段落摘录 + 本地统计值）、`suggestion`（可执行修改）、`verdict_status`。

写 `/app/output/result.json`（动态纳入 case.json 全部 output_contract 字段 + `case_id`、`status`、`guideline_basis`、`checklist_results`、`findings`、`uncertainty`、`not_reviewed`、`change_log`）与 `/app/output/audit_report.md`。

## 误报抑制规则

- 无阈值依据不报"超限"；无指南依据不报"缺项"；
- 预印本/非投稿材料（如报告、slides）：结构类检查按 `不适用` 处理，只报声明完整性与许可问题；
- 章节命名变体（"Materials and Methods" vs "Methods"）不算缺失，按语义匹配；
- 摘要字数统计按脚本值，注明统计口径（去参考文献/去标题），不同口径差异说明在 `uncertainty`；
- 任何判定回指逐字摘录与指南条目；做不到就 `待复核`。

## 异常处理

| 情况 | 处置 |
|-|-|
| 目标期刊缺失 | 退化到通用核心清单，`guideline_basis` 注明，数值阈值项标 `待复核` |
| 指南检索不到 | 同上，并记录已尝试的检索式 |
| PDF 无法解析/缺页 | 可解析部分照核，`partial`，相关条目标 `not_reviewed` |
| 统计值与指南口径不一致（如是否含图注字数） | 两种口径都算出并说明，判定时取与指南口径一致者；无法确定标 `待复核` |

## 最小调用示例（示意，非正式案例结果）

```bash
python3 /skills/weekly-skill/scripts/manifest_stats.py /app/work/paper.txt /app/work/stats.json
python3 /skills/weekly-skill/scripts/declaration_inventory.py /app/work/paper.txt /app/work/decl.json
# 随后按 SKILL.md phase 3-5：拆指南条目 + 逐条映射 + 写 result.json
```

示意 finding（标注为示例）：

```json
{"id": "F3", "type": "declaration_incomplete", "severity": "major",
 "location": {"file": "paper.pdf", "page": 12, "section": "Declarations", "quote": null},
 "evidence": "通用核心清单 item D3（Data Availability Statement）；脚本 inventory：decl.data_availability.present=false",
 "suggestion": "补充数据可用性声明：数据仓库名+DOI，或说明受限原因与申请途径",
 "verdict_status": "确认"}
```

## 资源清单

- `scripts/manifest_stats.py`：稿件结构与数值统计（纯 stdlib）
- `scripts/declaration_inventory.py`：声明清单扫描
- `references/checklist_core.md`：通用核心检查清单（无目标期刊时使用）
- `references/guideline_sources.md`：常见出版商作者指南检索入口与版本记录方法
- `references/severity_rubric.md`：类型与严重度分级
- `examples/minimal_example.md`：完整运行示意
