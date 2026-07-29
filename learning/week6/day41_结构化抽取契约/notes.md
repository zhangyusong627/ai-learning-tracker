# Day 41：结构化抽取契约（AI 环节）

## 学习日期

2026-07-29

## 学习目标与边界

目标：理解金融机构接入 Skill 中，为什么不能让 AI 直接根据资方文档生成 `FundManagerImpl`，而必须先生成一份可校验、可追溯、可人工确认的中间契约。

不学习：

- 不展开完整 Agent（智能体）编排；
- 不生成完整 Java 项目；
- 不接真实金融机构；
- 不使用前公司代码、内部文档、真实字段、配置、日志或测试数据。

## 核心结论

AI 不能直接生成 `FundManagerImpl`。正确链路是：

```text
资方接入文档
→ 解析成标准文档块
→ AI 抽取候选契约
→ 程序做结构校验
→ 人工确认关键业务判断
→ approved 契约
→ 生成 FundManagerImpl 骨架
→ 编译、契约测试、人工 Review
```

原因是：

- 结构正确不代表业务正确；
- 模型置信度高不代表事实正确；
- 有证据不代表证据真的支持该业务结论；
- 资方接入中的字段映射、接口选择、流程编排、必传字段、阶段依赖和配置变量都会影响真实业务结果。

## 术语

- `LLM`：Large Language Model，大语言模型。
- `Skill`：技能，指可复用的任务能力或工作流。
- `FundManagerImpl`：资金机构接入 SPI 实现类骨架，用于承载具体资方的授信、借款、还款、合同、对账等接入逻辑。
- `SPI`：Service Provider Interface，服务提供者接口，用于让不同资方实现同一套平台接口。
- `candidate`：候选结果，模型认为可能正确，但还没有被确认。
- `approved`：已批准结果，经过人工确认，可以进入后续生成链路。
- `unresolved`：未解决结果，证据不足、冲突或条件不明确，必须阻断后续生成。
- `evidence`：证据，记录结论来自哪份文档、哪个版本、哪个章节或表格位置。
- `stage_dependencies`：阶段依赖，后一个业务阶段依赖前一个业务阶段的返回值。

## 双向字段映射模型

用户纠正并确认：资方接入不是单向字段抽取，而是双向映射。

```text
请求报文方向：
平台标准字段 -> 资方个性化字段

返回报文 / 回调方向：
资方个性化字段 -> 平台标准字段
```

因此契约中应避免使用容易混淆的 `source_field / target_field`，改为：

- `mapping_direction`：映射方向；
- `platform_field`：平台标准字段；
- `institution_field`：资方个性化字段。

## 四类核心对象

结构化抽取契约不是普通 JSON 示例，而是 `FundManagerImpl` 生成前的安全中间层。至少应覆盖：

- `operations`：业务阶段，例如授信申请、授信查询、借款申请、放款查询、还款、对账。
- `variables`：配置变量，例如接口地址、商户号、产品号、加密配置、文件配置、超时时间。
- `field_mappings`：字段映射，包括请求方向和返回方向。
- `stage_dependencies`：阶段依赖，例如借款申请依赖授信申请或授信查询返回的 `applyId`。

## 阶段依赖

用户解释：

```text
如果下一个接口依赖上一个接口的返回值，那么上一个接口应该按照统一规范把资方返回的关键业务字段记录下来；下一个接口从这个保存的位置统一获取。
```

整理后的工程表达：

```text
跨阶段依赖字段不能散落在各个接口的临时代码里。
前序接口必须按照统一规范，把资方返回的关键业务字段提取、归一化并持久化到约定位置。
后续接口再从这个约定位置读取，而不是重新猜、重新解析或依赖某个接口的私有实现。
```

示例：

```text
creditApply / queryCredit 返回 applyNo
loanApply 请求字段 creditApplyNo 需要使用该 applyNo
```

这不仅是普通字段映射，还必须记录阶段依赖，因为该字段取值来自上一个业务接口的返回值。

## 配置变量

用户解释：

```text
测试环境、集成环境、预发环境、生产环境配置不同，不能把接口地址、商户号、产品号、加密配置硬编码到业务逻辑代码中。
这些值应通过配置注入，例如 Apollo 配置中心，并在初始化阶段做必填校验。
```

补充结论：

- 配置变量缺失应在 `initialize` 阶段失败；
- 不能等到真实请求资方时才发现配置为空；
- 缺失或错误配置可能导致请求发错环境、签名失败、加密失败、文件上传失败或回调验签失败。

## 转换规则

转换规则解决的是平台字段和资方字段之间值格式不同的问题，例如：

- 金额单位转换；
- 枚举映射；
- 日期格式转换；
- 字符串拼接或拆分。

规则：

```text
LLM 只能输出已注册的转换规则名称；
不能输出自由 Java 代码；
任何 transformation_code / java_code 字段都应触发拒绝生成。
```

原因：

- 正确性没法保障；
- 存在安全风险；
- 可维护性和可验证性差。

## 项目改造结果

本节学习过程中，独立作品集仓库已完成本地改造，路径：

```text
/Users/zhangyusong/Documents/AICoding/financial-institution-integration-skill
```

关键调整：

- 将契约模型从 `standard_field / source_field` 调整为 `platform_field / institution_field / mapping_direction`；
- 新增 `operations`、`variables`、`stage_dependencies`；
- Java 模板从 `InstitutionAdapter` 调整为 `FundManagerImpl` 风格骨架；
- 校验脚本增强为检查四类对象，并拒绝自由代码字段。

验证命令：

```bash
python3 -m py_compile skill/integrate-financial-institution/scripts/*.py
python3 skill/integrate-financial-institution/scripts/validate_mapping.py fixtures/synthetic_mapping.json --require-approved
git diff --check
```

验证结果：

```text
VALID: 2 mapping(s) for Synthetic Aurora Finance @ 2026-07-demo (2 operation(s), 1 variable(s), 1 stage dependency/dependencies)
```

## 三层测试结果

### 1. 概念理解

问题：为什么“LLM 输出结构正确 + confidence 很高 + 有 evidence”仍然不能直接进入代码生成，还必须经过人工批准？

用户回答：

```text
因为结构化正确不代表业务正确，所以需要人工确认它的事实是否一致，也就是事实一致性校验还得人工来。
```

评价：正确。

### 2. 流程诊断

问题：如果生成逻辑把 `candidate + confidence > 0.95` 当成可生成条件，最大问题是什么？

用户回答：

```text
候选结果有且自信度比较高就直接让 AI 去生成 Java 代码，绕开了人工验证，这是不合理的。
```

评价：正确。

### 3. 场景迁移

问题：资方文档写 `loanApply.creditApplyNo` 必填，取值为 `creditApply.applyNo`，为什么不能只记录普通请求字段映射？

用户回答：

```text
还必须记录这个字段的来源，因为这个字段是跨接口的，依赖上一个接口的返回值，存在阶段依赖。
```

评价：正确。

## 掌握程度

- 领域与架构理解：★★★★☆
- 代码阅读与故障定位：★★★☆☆
- 独立实现能力：★★★☆☆
- 新场景迁移能力：★★★★☆

依据：

- 能纠正字段映射方向，并明确请求方向与返回方向不同；
- 能解释阶段依赖的业务含义；
- 能解释配置变量不能硬编码；
- 能识别 `candidate + high confidence` 绕过人工审核的问题；
- 代码实现目前主要由 Codex 完成，后续仍需通过阅读改造后的脚本和模板来提升独立实现能力。

## 持续误区与修正

- 误区：把结构化抽取契约理解成一组 JSON 字段细节。
- 修正：契约的本质是 AI 输出和 Java 骨架生成之间的安全中间层。
- 识别线索：如果讨论开始长时间停留在字段名、JSON 细节、证据格式上，而没有回到“能否安全生成 FundManagerImpl”，说明学习已经偏细。

## 下一步

继续 Week 6 的最小纵向闭环：

```text
synthetic 文档
→ 统一解析
→ 标准文档块
→ 结构化契约
→ approved 样例
→ FundManagerImpl 骨架模板
→ 校验脚本
```

下一次重点不再继续问抽象概念，而是阅读改造后的 `validate_mapping.py` 和 `FundManagerImpl.java.tmpl`，确认代码如何落实今天的契约边界。

## 延迟复习

- Day +1：2026-07-30，不看笔记复述“为什么不能让 AI 直接生成 FundManagerImpl”。
- Day +7：2026-08-05，给一个新资方接口场景，判断哪些是字段映射，哪些是阶段依赖，哪些是配置变量。
- Day +30：2026-08-28，用面试语言讲清楚这个 Skill 项目的业务价值、AI 边界和工程闸门。

