---
name: cite-verify-audit
description: >-
  引用真实性核验 (citation integrity audit)。当且仅当对一份论文或科研材料执行
  引用规范审查时使用本技能：核对参考文献是否真实存在、元数据（作者/年份/期刊/
  DOI）是否与原文一致、正文论断与所引文献是否一一对应（引而不证、张冠李戴），
  并识别格式不统一与重复引用。本技能把审查固定为五个相位：preflight 锁定输入与
  初始 result.json；extract 用脚本确定性切分参考文献表并抓取正文引文语境；
  screen 做本地格式与一致性初筛；verify 在严格预算内联网逐条核验文献真实性与
  元数据；compose 产出逐条问题（原文定位+判定依据+严重度+修改建议）并写入
  /app/output/result.json。不核验隐私、伦理或投稿格式问题。Use when: auditing
  the references and in-text citations of a paper for existence, metadata
  accuracy, claim-citation correspondence, and format consistency.
---

# 引用真实性核验 cite-verify-audit

## 用途与适用条件

对一份论文/预印本/科研材料做**引用规范审查**，回答四个可核对的问题：

1. 每条被引文献是否**真实存在**；
2. 参考文献表中的元数据（作者、年份、期刊/会议、卷期页、DOI）是否与真实文献**一致**；
3. 正文论断与所引文献是否**一一对应**——识别引而不证（引文不支持论断）、张冠李戴（论断内容与文献主题不符）；
4. 参考文献列表内部是否**格式统一**、有无重复条目、缺字段或未来年份等明显异常。

适用条件（全部满足才启用）：

- 平台提供 `/input/case.json`（含 `case_id`，可能含 `task`/`output_contract`）与 `/input/task.md`，源材料（PDF 等）在 `/input` 下；
- 工作目录 `/app/work`，交付目录 `/app/output`；
- 任务属于引用规范/文献核验/事实核查类审查。

不在本技能范围：隐私与个人信息审查、伦理审批审查、投稿格式与期刊指南核对、语言润色、数据重新分析。若 `case.json` 指定的审查面与本技能无关，仍执行本技能的引用审查并在 `scope_note` 中如实说明范围偏差；case.json 要求的其他审查面标记为 `未检查`（见 phase 5）。

## 依赖

- **仅 Python 3 标准库**（3.8+）。严禁依赖 numpy/pandas 等第三方包，即使环境已安装。
- `pdftotext`（poppler）：可选。**缺失时优雅退化**——preflight 记录工具不可用，若 `/input` 已提供抽取文本（`.txt`/`.md`）则直接使用；两者皆无时产出 `status: "blocked"` 的诚实结果并说明原因，不编造引用内容。
- 联网检索能力（浏览器或 web 工具）：用于 phase 4 文献核验。**检索不可用**时把所有联网核验项标记 `待复核`，本地可判定的条目（格式、重复、缺字段、年份异常）照常给出结论。

## 运行相位

### phase 0 preflight（必须先做，锁定部分结果）

1. 读取 `/input/case.json`：记录 `case_id`、任务描述、`output_contract` 字段列表；把 contract 字段原样纳入最终 result.json。
2. 列出 `/input` 下材料；对 PDF 运行 `pdftotext -layout <pdf> /app/work/paper.txt`，按 `\f`（换页符）切分记录页码。
3. 立即写入 `/app/output/result.json`：`status: "partial"`、`case_id`、已完成相位、已用工具及版本、异常记录。此后任何中断都留有诚实部分结果。

### phase 1 extract（脚本确定性抽取）

依次运行（脚本均为"显式输入→显式输出"，失败返回非零码）：

```bash
python3 <skill>/scripts/extract_refs.py /app/work/paper.txt /app/work/refs.json
python3 <skill>/scripts/extract_citations.py /app/work/paper.txt /app/work/citations.json
```

- `refs.json`：参考文献条目列表，每条含序号、原文、起始页、以及脚本正则抽取的字段初值（作者/年份/标题/期刊/DOI 猜测）。
- `citations.json`：正文引文标记列表，每条含标记原文、所在页、所在句（前后各约 120 字符语境）、解析出的引用序号列表。

若参考文献表切分为 0 条但正文存在引文标记，检查 `paper.txt` 编码与章节标题（"References"/"参考文献"/"REFERENCES"/"Bibliography"），人工（agent）修正切分点后重跑；仍失败则记录异常，引用条目数按 0 处理并如实说明。

### phase 2 screen（本地一致性初筛，不耗联网预算）

```bash
python3 <skill>/scripts/lint_refs.py /app/work/refs.json /app/work/lint.json
```

- 重复条目检测：标题归一化后的相似度（脚本内实现）；
- 缺字段：无年份、无作者、无期刊/会议名；
- 年份异常：晚于当前年份，或与 DOI 注册年份明显冲突；
- 格式混用：同一文献表内数字编号体例与作者-年份体例混杂；
- DOI 形态校验（`10.xxxx/...` 前缀与非法字符）。

lint 结果只产生**候选**问题；是否升级为 findings 由 phase 4/5 结合原文判断（例如"无 DOI"在人文期刊是惯例，不得直接判违规）。

### phase 3 引文-论断对应初判（模型逐条判断，绑定原文）

对 `citations.json` 中每个引文标记：读出所在句与其参考文献条目原文，判断该句论断**是否需要一个文献支撑**（事实性、归因性论断需要；常识、方法自述、本文结果不需要）。对需要支撑者，判断条目主题与论断是否明显无关（张冠李戴候选）或显然无法支撑（引而不证候选）。输出初判表，**不确定的一律标 `待复核`**，不得凭学科印象定罪。

### phase 4 verify（联网核验，严格预算纪律）

预算纪律（硬约束，防止超时）：

- 最多 **12 次**检索请求，全部用于优先级最高的条目；优先级 = （正文核心结论所引 > 方法关键所引 > 背景所引）且（年份可疑/期刊可疑/作者拼写异常 > 正常条目）。
- 每条文献一次检索内完成"存在性 + 元数据比对"；不允许对同一条目重复检索。
- 检索结果只采信可核对来源（出版社页、DOI 解析、PubMed/Crossref/arXiv 记录）；**只记录实际检索到的元数据**，与参考文献表逐项比对：作者序列、年份、期刊名、卷期页、DOI。任何字段不一致 → `metadata_mismatch`。
- 未检索到（可能真实但未被索引，或检索词失败）：标 `待复核`，注明已尝试的检索式；**严禁**把"没搜到"直接判为"文献不存在"。同一文献需两个独立信号（如检索无结果 + DOI 无法解析）才可判 `fabrication_suspected`，且判定时必须写明证据链。

### phase 5 compose（结构化交付）

合并 lint 候选、phase 3 初判与 verify 结果，产出 findings。每条 finding 必须包含：

- `id`、`type`：`fabrication_suspected` / `metadata_mismatch` / `claim_citation_mismatch` / `unsupported_claim` / `duplicate_reference` / `format_inconsistency` / `missing_field` / `suggestion`；
- `severity`：`critical`（疑似捏造、结论性论断引而不证）/ `major`（元数据错误、张冠李戴）/ `minor`（格式、缺 DOI 等非实质问题）/ `info`（建议）；
- `location`：材料文件名 + 页码 + 章节 + 逐字摘录（引用条目原文或正文句子，不得改写）；
- `evidence`：判定依据——本地规则名（lint 检查项）或检索来源（数据库名 + 检索到的元数据原文）；
- `suggestion`：可执行修改建议（补 DOI、改为正确文献、删除 unsupported 引注、统一体例等）；
- `verdict_status`：`确认` / `待复核`，及理由。

严重度分级细则见 `references/severity_rubric.md`；引用体例规则（GB/T 7714、Vancouver、APA 等常见体例的判定特征）见 `references/style_guides.md`。

写入 `/app/output/result.json`（动态纳入 case.json 的全部 `output_contract` 字段，外加 `case_id`、`status`、`findings`、`evidence_sources`、`uncertainty`、`not_reviewed`、`change_log`）与 `/app/output/audit_report.md`（人读报告，逐条问题+定位+依据+建议）。`status` 取值为 `complete` / `partial` / `blocked`，不得虚报。

## 误报抑制规则（必须遵守）

- 风格差异 ≠ 违规：体例与目标期刊要求不符时才报 `format_inconsistency`，并说明目标体例；
- 人文社科文献无 DOI 是惯例，不单独作为问题；
- 预印本、会议论文、报告、标准各自合法存在形式，不得因"不是期刊论文"判 fabricated；
- 作者姓名拼写变体（如 von/der、连字符）不构成 metadata_mismatch，除非伴随其他字段冲突；
- 任何判定必须能回指原文逐字摘录与可核对依据；做不到就降为 `待复核`。

## 异常处理

| 情况 | 处置 |
|-|-|
| PDF 无法解析/缺页 | 记录缺页区间；能解析部分照常审查，结果 `partial`，缺页涉及的引用标 `not_reviewed` |
| 无参考文献表（如短文、新闻稿） | 正文引文语境仍审查；references 相关检查标 `not_reviewed` 并说明 |
| 联网不可用 | 本地结论照出，所有存在性/元数据核验项标 `待复核` |
| 引用标记与文献表序号无法对应（如文中用作者-年份、表用编号） | 建立映射表后再判断；映射失败项标 `待复核` |
| 超预算风险 | 达到 12 次检索上限立即停止，剩余条目统一标 `待复核-未核验` |

## 最小调用示例（示意，非正式案例结果）

```bash
# 输入：/input/case.json、/input/task.md、/input/paper.pdf
python3 scripts/extract_refs.py /app/work/paper.txt /app/work/refs.json
# → {"reference_count": 34, "entries": [{"index": 1, "raw": "Wang L, et al. ...", "page": 9, "year": "2021", "doi": null}, ...]}
python3 scripts/lint_refs.py /app/work/refs.json /app/work/lint.json
# → {"candidates": [{"index": 7, "issue": "duplicate_of", "other_index": 12, ...}, ...]}
```

示意输出（节选，标注为示例）：

```json
{"case_id": "example", "status": "complete",
 "findings": [{"id": "F1", "type": "metadata_mismatch", "severity": "major",
   "location": {"file": "paper.pdf", "page": 9, "section": "References",
     "quote": "Zhang Y, Li H. Deep ... Nature. 2019;571:123-130."},
   "evidence": "Crossref 记录显示该文年份为 2020、卷 580、页 45-52（检索于本次运行）",
   "suggestion": "按 Crossref 记录更正年份、卷、页；补 DOI 10.xxxx/xxxxx",
   "verdict_status": "确认"}]}
```

## 资源清单

- `scripts/extract_refs.py`：参考文献表切分与字段抽取（纯 stdlib）
- `scripts/extract_citations.py`：正文引文标记定位与语境抓取
- `scripts/lint_refs.py`：本地一致性初筛（重复/缺字段/年份异常/体例混用/DOI 形态）
- `references/severity_rubric.md`：finding 类型与严重度分级
- `references/style_guides.md`：常见引用体例判定特征与"何时算违规"
- `examples/minimal_example.md`：完整一次运行的输入/输出示意
