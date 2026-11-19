# Finding 类型与严重度分级（cite-verify-audit）

## 类型定义

| type | 含义 | 成立的判定门槛 |
|-|-|-|
| fabrication_suspected | 文献疑似不存在（捏造） | 两个独立信号同时成立：检索系统（学术索引/搜索引擎）无结果 + DOI 无法解析或指向其他文献。缺一不可，判定时写明证据链。 |
| metadata_mismatch | 元数据与真实文献不一致 | 检索到的权威记录（出版社页、Crossref、PubMed）与参考文献表在作者序列、年份、期刊名、卷期页、DOI 任一字段冲突。 |
| claim_citation_mismatch（张冠李戴） | 所引文献主题与正文论断无关 | 文献标题/摘要主题与论断关键词域明显不同，且通读语境后无合理支撑关系。 |
| unsupported_claim（引而不证） | 论断需要支撑而所引文献明显不能支撑 | 论断为事实性/归因性结论，所引文献类型（如评论、方法学、不相关数据集）明显无法提供该结论；或引用标记落在无实质内容的承接句。 |
| duplicate_reference | 文献表内重复条目 | 同 DOI，或标题高度重合且作者、年份一致。 |
| format_inconsistency | 体例不统一 | 同一文献表内编号体例与作者-年份体例混杂；或同一字段（页码范围、et al. 截断、期刊缩写）处理方式不一致；判定时必须说明所对照的目标体例（来自投稿要求或文献表自身主流体例）。 |
| missing_field | 条目缺字段 | 缺年份（永远成立）、缺卷期页（仅在目标体例要求时成立，否则降为 suggestion）。 |
| suggestion | 建议性意见 | 可提升规范性但不构成违规：补 DOI、统一大小写、建议引用更新的综述等。 |

## 严重度

| severity | 适用 |
|-|-|
| critical | fabrication_suspected；支撑核心结论的引而不证/张冠李戴 |
| major | 一般论断的 metadata_mismatch、claim_citation_mismatch、unsupported_claim、duplicate_reference |
| minor | format_inconsistency、missing_field、局部体例冲突 |
| info | suggestion |

## 判定纪律

1. 每条 finding 附逐字摘录（不得改写原文）与可核对依据（本地规则名或检索来源+检索到的元数据）。
2. 证据不足一律 `待复核`，并写明还缺什么证据。
3. 风格差异、学科惯例（如人文文献无 DOI）、作者姓名拼写变体不构成违规。
4. 优先保证零漏报真实风险与零误报之间的平衡：宁可多一条 `待复核`，不可把未核实内容写成 `确认`。
