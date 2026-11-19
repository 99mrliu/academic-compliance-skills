# 常见引用体例判定特征

本文件只用于**识别体例**与判断**内部一致性**，不代替任何期刊的具体投稿要求
（目标期刊要求以 case 材料或检索到的作者指南为准）。

## 数字顺序体例（Vancouver 系）

特征：正文 `[12]`、`[3,7]`、`(12)`；文献表按引用顺序编号；条目形如
`Wang L, Chen H. Title. J Name. 2021;12(3):45-52. doi:...`
常见变体：GB/T 7714-2015（中文期刊，`[J]`、`[M]`、`[C]` 文献类型标识）、
IEEE（方括号、缩写期刊名）。

## 作者-年份体例（Harvard/APA 系）

特征：正文 `(Wang & Chen, 2021)`、`Wang and Chen (2021) reported`；
文献表按作者字母排序；APA 7 条目形如
`Wang, L., & Chen, H. (2021). Title of the article. *Journal Name*, 12*(3)*, 45–52.`

## 脚注/尾注体例

正文上标数字，说明区或文末逐条给出；此时文献表可能无独立 References 标题，
切分失败属预期，应改按脚注区解析。

## "何时算违规"

- 同一文献表内混杂编号体例与作者-年份体例 → `format_inconsistency`（major 以下）。
- 全部条目统一使用某体例、仅个别条目字段缺失 → `missing_field`（minor），
  但仅当目标体例要求该字段时成立；无目标体例时降为 `suggestion`。
- 条目内部中英文名混排、全半角标点混用 → 记录为 `suggestion`，
  除非投稿要求明确规定。
- 期刊名缩写与全称混用 → `format_inconsistency`（minor），前提是该表主流
  采用其中一种。

## 参考文献

- GB/T 7714-2015《信息与文献 参考文献著录规则》。
- ICMJE Recommendations（Vancouver 体例来源），https://www.icmje.org/recommendations/。
- APA Publication Manual, 7th ed. (2020)。
- IEEE Reference Style Guide。
