# Finding 类型与严重度分级（venue-compliance-check）

## 类型定义

| type | 含义 | 成立门槛 |
|-|-|-|
| missing_item | 必备项缺失 | 指南/清单明确要求 + 脚本 inventory 或全文复核确认不存在。 |
| over_limit | 超限 | 指南给出阈值 + 脚本统计值（注明口径）超出；口径不一致时标待复核。 |
| format_conflict | 格式冲突 | 稿件体例与指南明确要求冲突（如双盲却署名、要求结构式摘要却为非结构式）。 |
| licensing_gap | 第三方材料来源/许可不清 | 图/表/代码/数据集缺少来源或版本标注，且无法从材料确认全部自绘/自产。 |
| anonymization_breach | 双盲匿名化破坏 | 指南要求双盲 + 正文出现作者姓名/单位/邮箱/可识别致谢。 |
| declaration_incomplete | 声明不完整 | 声明存在但内容缺要素（如批件无编号、数据声明无获取途径）。 |
| suggestion | 建议性意见 | 提升规范性但不构成违规（如补 ORCID、统一图注格式）。 |

## 严重度

| severity | 适用 |
|-|-|
| critical | anonymization_breach（直接破坏评审匿名性）；必备声明系统性缺失（无 Ethics 且涉人/涉动物） |
| major | missing_item（必备章节/声明）、over_limit（硬性上限）、declaration_incomplete（批件/数据路径缺要素） |
| minor | format_conflict（非硬性）、licensing_gap（个别图注缺来源） |
| info | suggestion |

## 判定纪律

1. 每条 finding 附：指南条目 id/摘录 + 稿件侧证据（脚本统计值或逐字摘录）。
2. 无指南依据不判 missing/over_limit；无阈值依据不判 over_limit。
3. 章节命名变体按语义匹配，不判缺失。
4. 证据不足标 `待复核`，写明缺什么。
