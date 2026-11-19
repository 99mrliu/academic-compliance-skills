# 作者指南检索与版本记录（venue-compliance-check）

## 获取优先级

1. case 材料中附带的指南文本（最优先，直接拆条）；
2. 材料中指定的指南文件名（在 /input 下查找）；
3. 联网检索目标期刊/会议的官方作者指南（最多 3 次检索）；
4. 退化：`checklist_core.md` 通用核心清单。

## 检索要点

- 只采信出版商/会议官网页面；搜索引擎摘要、第三方转载不作为依据。
- 记录：**页面 URL、页面注明的版本/更新日期、检索日期**；写入
  result.json 的 `guideline_basis`。
- 拆条时逐条摘录指南原文（逐字），不得凭印象改写阈值。

## 常见官方入口（供检索定位，不作为条款本身）

- Nature Portfolio: https://www.nature.com/ 各刊 "Submission guidelines"
- Science: https://www.science.org/ "Information for Authors"
- Elsevier: 各刊主页 "Guide for Authors"
- Springer: 各刊 "Submission guidelines"
- IEEE: https://journals.ieeeauthorcenter.ieee.org/
- ACM: https://www.acm.org/publications/authors/submissions
- ICML/NeurIPS 等会议: 当年 CfP 页面

## 检索不到时

在 `guideline_basis` 写明尝试过的检索式与结果，退化到通用核心清单，
需要阈值的项目标 `待复核`。严禁编造阈值或条款编号。
