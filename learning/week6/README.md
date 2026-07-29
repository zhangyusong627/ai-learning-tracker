# Week 6 - 金融机构接入 Skill：最小业务闭环

## 本周目标

从已有项目脚手架继续，实现自造文档、统一解析、标准文档块、结构化抽取和最小纵向闭环。RAG 延迟复习每天最多 30 分钟，不再占用完整学习日。

## 课程安排

| 日期 | 时间 | 主题 | 必须产出 |
|---|---:|---|---|
| 7.27 周一 | 7h | Day 36 RAG 全链路验收 | ✅ 完成 |
| 7.28 周二 | 7h | 脚手架审查 + V0.1 验收冻结 | ✅ 完成 |
| 7.29 周三 | 7h | 三个虚构机构的多格式文档 | ✅ 完成 |
| 7.30 周四 | 7h | 统一解析器 + ParseResult | ✅ 完成 |
| 7.31 周五 | 7h | 标准文档块 + 数据质量闸门 + 解析校验 | ✅ 完成 |
| 8.1 周六 | 4h | 结构化抽取契约（AI 环节） | ⏳ 待学习 |
| 8.2 周日 | 4h | 最小纵向闭环 + 自动测试 | ⏳ 待学习 |

## 当前证据索引

截至 2026-07-29，页面进度口径为 Week 6 已完成 5/7。证据分布如下：

- Day 36 RAG 全链路验收：本仓库已保留笔记和代码，见 `day36_RAG全链路集成/`。
- Skill 脚手架、自造文档、统一解析器、标准文档块和质量门禁：产物在独立作品集仓库 `/Users/zhangyusong/Documents/AICoding/financial-institution-integration-skill`，当前本地提交为 `252ab46 feat: scaffold financial institution integration skill`。
- 已验证命令：`python3 skill/integrate-financial-institution/scripts/validate_mapping.py fixtures/synthetic_mapping.json --require-approved`，结果为 `VALID: 1 mapping(s) for Synthetic Aurora Finance @ 2026-07-demo`。

状态口径：作品集产物已经生成并通过最小确定性校验；后续学习继续时，仍要按 `LEARNING_WORKFLOW.md` 补齐用户自己的架构复述、失败路径解释、三层测试和复盘，不能仅凭代码存在判定为掌握。

## 通过标准

- 不依赖前公司代码、内部文档、真实字段或生产数据；
- 三种格式至少形成可复现的自造输入；
- 部分成功不会被伪装成完整成功，需要 OCR 时明确中止后续入库；
- 标准文档块保留来源和版本，抽取事实必须绑定证据；
- 最小闭环有自动测试和至少一个失败案例。
