# Finding 类型与严重度分级（privacy-ethics-audit）

## 类型定义

| type | 含义 | 成立门槛 |
|-|-|-|
| pii_exposure | 可识别个人信息暴露 | 直接标识符或可重识别准标识符组合存在于材料中，且不属于正当署名/引用信息。 |
| consent_missing | 涉人数据但无知情同意声明 | 材料使用个体级人类数据，全文无 consent 段落（脚本确认 absent + agent 全文复核）。 |
| consent_scope_mismatch | 同意范围不覆盖实际使用 | consent 存在，但材料实际将数据公开/对外共享，而同意书未覆盖发表/公开共享。 |
| ethics_approval_missing | 缺伦理审批声明 | 涉人/涉动物研究无伦理审批声明（或批件编号缺失且未说明豁免依据）。 |
| ethics_scope_mismatch | 批件范围不覆盖实际数据类型 | 批件编号存在但注明适用范围，而材料数据类型（如回顾性病历、新增样本类型）超出该范围；无证据时不得臆断，须标待复核。 |
| data_availability_conflict | 数据可用性声明与实际矛盾 | 声称公开但无获取途径；声称匿名但材料留直接标识符；受控数据无访问说明。 |
| animal_welfare_missing | 动物实验缺审批/福利声明 | 有动物实验描述但无动物伦理批件与福利规范声明。 |
| deidentification_suggestion | 脱敏/改写建议 | 信息本身可保留但应降精度或改写（精确日期→年龄段、医院+日期→笼统表述）。 |
| suggestion | 其他建议 | 补充声明模板、完善注册号等。 |

## 严重度

| severity | 适用 |
|-|-|
| critical | pii_exposure 中直接标识符（身份证号、电话、病历号、姓名+病历）暴露且无 consent/批件覆盖；data_availability_conflict 中"声称匿名但留直接标识符" |
| major | consent_missing、ethics_approval_missing、animal_welfare_missing、consent_scope_mismatch、data_availability_conflict（声称公开无路径） |
| minor | 声明措辞模糊、批件编号格式缺失、部分声明缺位（如缺 AI 使用声明） |
| info | deidentification_suggestion、suggestion |

## 判定纪律

1. 每条 finding 附逐字摘录与条款条目（名称+条款号）。
2. 作者署名信息、公开文献引用姓名、占位符/示例不报。
3. 批件存在性无法确认时标 `待复核`，不得判批件无效。
4. 宁可多一条 `待复核`，不把未核实内容写成 `确认`。
