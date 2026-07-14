# AI 学习代码与笔记

本目录统一保存 90 天 AI 学习计划的课程代码、笔记和可复现示例。

所有课程统一遵循 [项目学习闭环规范](LEARNING_WORKFLOW.md)。该规范覆盖课前诊断、理论讲解、实践、测试、评估、复盘和延迟复习。

## 目录

| 周次 | 主题 | 入口 |
|---|---|---|
| Week 1 | Python 基础、FastAPI、AI API | [week1-python/README.md](week1-python/README.md) |
| Week 2 | 大模型基础与 Prompt Engineering | [week2/README.md](week2/README.md) |
| Week 3 | LangChain 与聊天助手 V2 | [week3/README.md](week3/README.md) |
| Week 4 | Embedding、向量数据库、微调与文档处理 | [week4/README.md](week4/README.md) |

## 结构约定

- 每周使用独立目录，包含周进度 `README.md`。
- 每天使用独立课程目录，包含 `notes.md` 和对应实践代码。
- 源码、笔记、依赖清单、`.env.example` 和必要的小型测试文件纳入 Git。
- `venv/`、`.env`、缓存、聊天记录、向量数据库和其他运行产物不纳入 Git。
- 示例代码通过环境变量读取 API Key，仓库中不得出现真实密钥。
- 每日课程必须执行 `LEARNING_WORKFLOW.md` 中的九阶段闭环，并把掌握证据和复盘写入当天 `notes.md`。
- 流程问题先记录、再在下一课程验证；验证有效后更新规范，最终再抽象为跨领域 Learning Skill。

## Python 环境

课程虚拟环境不提交到 Git。进入相应周目录后，根据依赖清单创建环境：

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

需要调用大模型 API 的周次，复制安全模板并填写本地密钥：

```bash
cp .env.example .env
```

`.env` 已被 Git 忽略；不要把真实密钥写入源码或 `.env.example`。
