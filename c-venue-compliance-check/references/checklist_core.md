# 通用核心检查清单（venue-compliance-check）

仅在**目标期刊/会议缺失或指南无法获取**时使用。本清单只收录多数出版商
共通的、可客观判定的项目；凡需要具体数值阈值的项目一律标 `待复核`。

## 结构类（S）

| id | 条目 | 判定依据 |
|-|-|-|
| S1 | 摘要存在且为独立段落 | stats.sections_detected 含 abstract |
| S2 | 关键词存在 | stats.keyword_count > 0 |
| S3 | 正文体例完整（IMRaD 或语义等价章节） | introduction/methods/results/discussion（或中文等价）均出现；章节命名变体按语义匹配 |
| S4 | 参考文献表存在 | stats.sections_detected 含 references |
| S5 | 摘要长度 | 无阈值依据 → 统计后标 `待复核`，附脚本值与口径 |

## 声明类（D）

| id | 条目 | 判定依据 |
|-|-|-|
| D1 | Funding 声明 | decl.funding.present |
| D2 | Conflict of Interest 声明 | decl.coi.present |
| D3 | Data Availability 声明 | decl.data_availability.present |
| D4 | Author Contributions 声明 | decl.author_contributions.present |
| D5 | 涉人研究的 Ethics + Consent 声明 | 材料含个体级人类数据时检查 decl.ethics 与 decl.consent |
| D6 | 涉动物研究的动物伦理声明 | 材料含动物实验描述时检查 decl.animal_welfare |
| D7 | 生成式 AI 使用声明（如使用了 AI 工具且致谢/方法中提及） | 出现 AI 工具使用痕迹但 decl.ai_use 缺失时提示 |

## 许可与来源标注类（L）

| id | 条目 | 判定依据 |
|-|-|-|
| L1 | 非自绘图表应有来源/许可标注 | 图注/表注出现 "reproduced/adapted/modified from"、"摘自"、"转载"、"permission" 等；若无法确认图表是否自绘，标 `待复核` 并列出无来源标注的图注清单 |
| L2 | 使用的第三方数据集应注明来源与版本 | 数据可用性声明或方法章节中数据集名 + 版本/访问日期 |
| L3 | 使用的第三方代码/软件应注明名称、版本、来源 | 方法章节软件名 + 版本号/引用 |

## 匿名化类（A，仅双盲要求时）

| id | 条目 | 判定依据 |
|-|-|-|
| A1 | 正文不得出现作者姓名、单位、邮箱 | declaration_inventory.anonymization_signals + 全文复核 |
| A2 | 致谢/基金中的可识别信息应暂缓或匿名化 | funding 声明内容复核 |

## 使用规则

1. 每条判定写 `guideline_basis`：本清单 id + 证据（脚本值或逐字摘录）。
2. 需要数值阈值的项目（字数、图表数、参考文献数上限）**不得臆造阈值**：
   报告统计值并标 `待复核-缺目标期刊阈值`。
3. 材料不是投稿稿件（报告、幻灯、数据集说明）时，S1–S5 按 `不适用` 处理，
   D/L 类仍适用。
