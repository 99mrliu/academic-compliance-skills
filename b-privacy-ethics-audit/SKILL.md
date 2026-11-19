---
name: privacy-ethics-audit
description: >-
  隐私、数据与伦理合规审查 (privacy, data-governance and ethics compliance
  audit)。当且仅当对论文/科研材料执行涉人数据合规审查时使用本技能：识别可识别
  个人信息（PII/PHI）、受限数据与未公开数据，核对知情同意、伦理批件编号与适用
  范围、数据可用性声明与受限数据访问说明的一致性，动物实验的规范声明，并给出
  可执行的脱敏与改写建议。流程固定为五个相位：preflight 锁定输入与初始
  result.json；extract 解析文本与章节；scan 用脚本做确定性 PII/敏感信息扫描；
  check 对照条款库核对同意、伦理、数据共享与动物实验声明；compose 产出逐条
  findings（原文定位+条款依据+严重度+脱敏建议）写入 /app/output/result.json。
  不审查引用真实性、投稿格式或语言质量。Use when: auditing a manuscript or
  research material for identifiable personal information, consent/ethics
  statements, data-availability compliance, and animal-experiment reporting.
---

# 隐私、数据与伦理合规审查 privacy-ethics-audit

## 用途与适用条件

回答四类可核对的合规问题：

1. 材料中是否存在**可识别个人信息**（PII/PHI：姓名+属性组合、身份证/证件号、电话、邮箱、住址、精确出生日期、住院号/病历号、罕见病+地域+年龄等可重识别组合、面部图像说明、基因组等生物识别数据）；
2. 涉人研究是否具备**知情同意**与**伦理审批**依据（批件编号、伦理委员会名称、豁免说明），且声明内容与数据使用范围一致；
3. **数据可用性声明**是否清楚、与实际共享的受限/未公开数据一致（声称公开却给不出获取途径，或声称已匿名却留直接标识符）；
4. 涉及动物实验时是否有**审批与规范声明**（动物伦理批件、ARRIVE 类要素）。

适用条件（全部满足才启用）：

- 平台提供 `/input/case.json` 与 `/input/task.md`，源材料在 `/input` 下；
- 工作目录 `/app/work`，交付目录 `/app/output`；
- 任务属于隐私、数据合规或伦理审查。

不在本技能范围：引用真实性核验、投稿格式核对、语言润色、法务或伦理委员会的正式意见（本技能只给出审查意见与改写建议，不替代审批）。若 `case.json` 指定的审查面与本技能无关，仍执行本技能的合规审查并在 `scope_note` 如实说明；其余审查面标 `未检查`。

## 依赖

- **仅 Python 3 标准库**（3.8+），严禁第三方包。
- `pdftotext`：可选。缺失时若 `/input` 有抽取文本则直接使用；皆无则产出 `status: "blocked"` 并说明。
- 不需要联网。条款依据来自 `references/clause_library.md`（随技能分发，标明名称、版本、发布日期）；如需核对目标期刊的具体数据政策且联网可用，可检索一次并在 evidence 中注明来源与日期。

## 运行相位

### phase 0 preflight（锁定部分结果）

读取 `/input/case.json`（`case_id`、任务描述、`output_contract`）；列出材料；`pdftotext -layout <pdf> /app/work/paper.txt` 并按 `\f` 记录页码；立即写 `/app/output/result.json`（`status: "partial"`、工具版本、异常记录）。

### phase 1 extract

```bash
python3 <skill>/scripts/locate_declarations.py /app/work/paper.txt /app/work/declarations.json
```

输出各声明的存在性与逐字摘录：知情同意（consent）、伦理审批（ethics/IRB）、数据可用性（data availability）、利益冲突（COI）、基金（funding）、动物实验（animal welfare）、作者贡献、AI 使用声明。不存在的声明本身就是候选缺失项。

### phase 2 scan（确定性敏感信息扫描）

```bash
python3 <skill>/scripts/scan_pii.py /app/work/paper.txt /app/work/pii.json
```

确定性正则+规则检测（每条命中给出**页码+逐字摘录+命中规则名**）：

- 直接标识符：邮箱、电话/手机号、身份证号（18 位含校验位规则）、IP 地址、银行卡式长数字、URL 内嵌用户名、病案/住院/门诊号样式；
- 准标识符组合：精确出生日期 + 地名 + 性别/年龄、医院名 + 科室 + 日期、"患者 张三"式称谓；
- 受限数据标记：人类遗传资源、基因组/转录组原始数据、临床试验注册号、受控访问数据库 ID（dbGaP/EGA/GEO controlled access 等）；
- 疑似未脱敏表格单元（姓名列、身份证列等）。

扫描结果是**候选**清单：每条必须由 agent 结合语境复核（例如作者单位邮箱属于正当署名信息，不报；示例/占位符不报）。

### phase 3 check（对照条款库逐条核对）

按 `references/clause_library.md` 的检查条目逐项判断（每条给出"通过/问题/待复核/不适用"）：

1. 涉人数据存在 → 是否有知情同意声明？声明是否覆盖数据共享方式（尤其公开数据/公开投稿同意）？
2. 是否有伦理批件编号与机构名称？批件适用范围是否覆盖本文数据类型（回顾性豁免须有明示）？
3. 数据可用性声明与实际数据性质是否矛盾（声称公开的可识别数据 / 声称匿名但留直接标识符 / 声称受控访问但无访问路径）？
4. 动物实验：是否有动物伦理批件与福利规范声明？
5. 已识别的 PII 候选（phase 2）是否得到 consent 声明覆盖？未覆盖 → 问题 + 脱敏建议。

### phase 4 compose（结构化交付）

每条 finding 含：`id`、`type`（`pii_exposure` / `consent_missing` / `consent_scope_mismatch` / `ethics_approval_missing` / `ethics_scope_mismatch` / `data_availability_conflict` / `animal_welfare_missing` / `deidentification_suggestion` / `suggestion`）、`severity`（critical/major/minor/info，细则见 `references/severity_rubric.md`）、`location`（文件+页码+章节+逐字摘录）、`evidence`（条款库条目名或声明原文摘录）、`suggestion`（可执行脱敏/改写文本，如"将精确出生日期改为年龄段'35–40 岁'"）、`verdict_status`（确认/待复核）。

写 `/app/output/result.json`（动态纳入 case.json 全部 output_contract 字段 + `case_id`、`status`、`findings`、`declarations_inventory`、`uncertainty`、`not_reviewed`、`change_log`）与 `/app/output/audit_report.md`。

## 误报抑制规则

- 作者署名、单位、通讯邮箱、ORCID 属于正当署名信息，不报 PII；
- 公开文献引用中出现的他人姓名不报；
- 统计汇总（"n=120，平均年龄 45±6"）不是 PII；**可重识别组合**（精确日期+小地域+罕见属性）才是；
- 占位符、示例数据、明显虚构信息不报，可记 `info`；
- 判 `critical` 前必须确认：标识符直接指向可识别个体 + 材料无 consent/批件覆盖；
- 任何判定回指逐字摘录与条款条目；做不到就 `待复核`。

## 异常处理

| 情况 | 处置 |
|-|-|
| PDF 无法解析/缺页 | 可解析部分照审，`partial`，缺页相关项标 `not_reviewed` |
| 材料为非涉人研究（纯方法/理论） | 扫描照跑；无涉人数据则明确报告"未发现涉人数据，相关检查不适用"，不得编造问题 |
| 声明存在但措辞模糊 | 报 `major` 以下问题并给出改写建议，不判批件无效 |
| 条款库未覆盖的辖区/场景 | 标 `待复核` 并说明缺哪类依据，不编造条款 |

## 最小调用示例（示意，非正式案例结果）

```bash
python3 /skills/weekly-skill/scripts/locate_declarations.py /app/work/paper.txt /app/work/declarations.json
# → {"consent": {"present": true, "page": 8, "quote": "All participants provided written informed consent..."}, ...}
python3 /skills/weekly-skill/scripts/scan_pii.py /app/work/paper.txt /app/work/pii.json
# → {"hits": [{"rule": "cn_id_number", "page": 5, "quote": "身份证 1101**********1234", ...}]}
```

示意 finding（标注为示例）：

```json
{"id": "F1", "type": "pii_exposure", "severity": "critical",
 "location": {"file": "paper.pdf", "page": 5, "section": "Table 2",
   "quote": "患者 张某某，身份证 110101199001011234，就诊于某三甲医院"},
 "evidence": "PIPL 第 28 条（敏感个人信息含医疗健康与特定身份）；材料无 consent 声明覆盖公开投稿",
 "suggestion": "删除身份证号；姓名改'患者 P05'；年龄改年龄段；并在数据可用性中说明已脱敏",
 "verdict_status": "确认"}
```

## 资源清单

- `scripts/scan_pii.py`：确定性敏感信息扫描（纯 stdlib）
- `scripts/locate_declarations.py`：声明段落定位与逐字摘录
- `references/clause_library.md`：条款库（赫尔辛基宣言、ICMJE、PIPL/GDPR、ARRIVE 2.0 等，含版本与日期）
- `references/severity_rubric.md`：类型与严重度分级
- `examples/minimal_example.md`：完整运行示意
