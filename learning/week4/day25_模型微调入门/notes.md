# Day 25: 模型微调入门：LoRA原理+Hugging Face

## 学习目标
- 理解什么是模型微调
- 学习 LoRA 原理：参数高效微调
- 了解 Hugging Face 生态
- 掌握微调的具体步骤和工具

## 学习时间
2026年7月4日

---

## 1. 今天要做什么？

### 微调概念
- 什么是微调？为什么需要微调？
- 微调 vs Prompt Engineering

### LoRA 原理
- 什么是 LoRA？
- 为什么 LoRA 能用更少参数达到好效果？

### Hugging Face
- Hugging Face 是什么？
- 如何使用 Hugging Face

---

## 2. 核心概念

### 2.1 什么是微调？

```
微调 = 让模型学会特定领域的知识

通用模型：什么都知道，但什么都不精
├── 回答 general 问题：没问题
└── 回答 医疗/金融 专业问题：不够准确

微调后：在特定领域更专业
├── 医疗模型：懂医学术语，回答更准确
├── 金融模型：懂金融知识，分析更专业
└── 法律模型：懂法律条文，解读更精准
```

### 2.2 微调 vs Prompt Engineering

| 方式 | 做什么 | 优点 | 缺点 |
|------|--------|------|------|
| Prompt Engineering | 优化提示词，不改模型 | 简单、快速 | 效果有限 |
| 微调 | 给模型输入新知识，改变模型 | 效果更好 | 需要数据和计算资源 |

```
Prompt Engineering：教你怎么问问题
微调：教模型新知识

类比：
├── Prompt：教学生怎么考试
└── 微调：教学生新知识
```

### 2.3 LoRA 是什么？

**全称**：Low-Rank Adaptation（低秩适配）

**一句话解释**：用更少的参数，让模型学会新技能

```
LoRA = Low-Rank Adaptation
├── Low = 低
├── Rank = 秩（数学概念）
├── Adaptation = 适配/调整
└── 低秩适配 = 用更少参数适配新任务
```

### 2.4 LoRA 的核心优势

```
1. 成本低
   ├── 只训练少量参数（原来的 3%）
   ├── 普通 GPU 也能训练
   └── 不需要多块昂贵的 GPU

2. 效果好
   ├── 接近全参数微调的效果
   ├── 保留模型原有的通用能力
   └── 在特定领域表现更好

3. 灵活
   ├── 可以针对不同任务训练不同 LoRA
   ├── 一个模型可以加载多个 LoRA
   └── 切换任务只需切换 LoRA
```

### 2.5 LoRA 底层原理

```
大模型权重矩阵 W：
├── 大小：4096 × 4096
├── 参数量：1600万
└── 训练成本：很高

LoRA 的做法：
├── 把 W 分解成两个小矩阵
├── W ≈ A × B
├── A：4096 × 64（小矩阵）
├── B：64 × 4096（小矩阵）
└── 参数量：52万（只有原来的 3%）

训练时：
├── 冻结原模型 W（不更新）
├── 只训练 A 和 B
└── 推理时：W + A × B
```

**类比**：

```
全参数微调：重新装修整个房子
├── 效果最好
├── 但费时费力费钱
└── 需要拆掉所有东西重来

LoRA：只换几个关键家具
├── 效果也很好
├── 但省钱省时间
└── 保留房子的整体结构
```

### 2.6 为什么 LoRA 有效？

```
假设：模型的权重矩阵是"低秩"的
├── 意思是：大部分参数是冗余的
├── 真正重要的参数很少
└── 所以用小矩阵就能近似

类比：
├── 一张高清图片
├── 其实大部分像素是重复的
├── 用压缩算法可以大幅减小体积
└── 但看起来还是差不多
```

### 2.7 Hugging Face 是什么？

**一句话解释**：AI 模型的 GitHub

```
GitHub：代码的托管平台
├── 上传代码
├── 下载代码
├── 分享代码
└── 协作开发

Hugging Face：AI 模型的托管平台
├── 上传模型
├── 下载模型
├── 分享模型
└── 微调模型
```

**Hugging Face 能做什么**：

```
1. 下载预训练模型
   └── GPT、BERT、LLaMA 等

2. 微调模型
   └── 用 LoRA 等方法

3. 分享模型
   └── 上传到 Hugging Face Hub

4. 使用模型
   └── 一行代码调用
```

---

## 3. 微调的具体步骤

### Step 1：准备数据

```
格式：问题-答案对

示例：
{"question": "感冒了怎么办？", "answer": "多休息、多喝水、严重时就医"}
{"question": "发烧多少度需要就医？", "answer": "超过38.5度建议就医"}

数量：几百到几千条
质量：准确、规范
```

### Step 2：选择基础模型

```
从 Hugging Face 下载：
├── Qwen（通义千问，中文好）
├── LLaMA（Meta，英文好）
├── ChatGLM（智谱，中文好）
└── 选择适合任务的模型
```

### Step 3：配置 LoRA

```python
from peft import LoraConfig

lora_config = LoraConfig(
    r=8,                          # 低秩维度
    lora_alpha=32,                # 缩放因子
    target_modules=["query", "value"],  # 要微调的层
    lora_dropout=0.1              # dropout
)
```

### Step 4：训练

```python
from peft import get_peft_model

# 加载模型
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-7B")

# 应用 LoRA
model = get_peft_model(model, lora_config)

# 开始训练（伪代码）
for batch in dataloader:
    outputs = model(batch)
    loss = compute_loss(outputs)
    loss.backward()
    optimizer.step()
```

### Step 5：评估

```
测试集验证：
├── 准确率
├── 回答质量
└── 人工检查

调整参数：
├── 如果过拟合：增加数据、减小学习率
└── 如果欠拟合：增加训练轮次、调整 LoRA 参数
```

### Step 6：部署

```
合并模型：
├── 把 LoRA 合并到原模型
├── 导出完整模型
└── 部署上线
```

---

## 4. 常用工具

### 微调框架

```
├── Hugging Face Transformers（最常用）
│   └── 官方库，功能完整
├── LLaMA-Factory（中文友好）
│   └── 支持中文模型，界面友好
└── PEFT（LoRA 实现）
    └── Hugging Face 官方 LoRA 库
```

### 数据处理

```
├── datasets（Hugging Face）
│   └── 数据加载和处理
└── pandas（通用）
    └── 数据清洗和分析
```

### 训练加速

```
├── DeepSpeed（微软）
│   └── 分布式训练
└── Accelerate（Hugging Face）
    └── 简化训练代码
```

---

## 5. 代码示例

### 使用 Hugging Face 加载模型

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# 加载模型和分词器
model_name = "Qwen/Qwen-7B-Chat"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 使用模型
inputs = tokenizer("你好", return_tensors="pt")
outputs = model.generate(**inputs)
print(tokenizer.decode(outputs[0]))
```

### 使用 PEFT 配置 LoRA

```python
from peft import LoraConfig, get_peft_model

# 配置 LoRA
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

# 应用 LoRA
model = get_peft_model(model, lora_config)

# 查看可训练参数
model.print_trainable_parameters()
# 输出：trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.0622
```

---

## 6. 实操任务

### 任务 1：理解微调流程（30分钟）

```python
# 写出微调的 6 个步骤
# 用自己的话解释每个步骤做什么
```

### 任务 2：配置 LoRA 参数（20分钟）

```python
# 修改以下参数，观察可训练参数的变化
lora_config = LoraConfig(
    r=4,        # 尝试 4, 8, 16, 32
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"]
)

# 运行 model.print_trainable_parameters()
# 观察 trainable% 的变化
```

### 任务 3：调研模型（20分钟）

```python
# 在 Hugging Face 上找一个中文模型
# 记录：模型名称、参数量、适用场景
# https://huggingface.co/models?language=zh
```

---

## 7. 测验

1. **微调和 Prompt Engineering 有什么区别？**
   答：微调是给模型输入新知识（改变模型），Prompt 是优化提示词（不改变模型）

2. **LoRA 的核心优势是什么？**
   答：成本低、效果好，只训练少量参数，保留原有通用能力

3. **Hugging Face 是什么？**
   答：AI 模型的托管平台，类似 GitHub 之于代码

4. **LoRA 的全称是什么？**
   答：Low-Rank Adaptation（低秩适配）

5. **微调的 6 个步骤是什么？**
   答：准备数据 → 选模型 → 配 LoRA → 训练 → 评估 → 部署

---

## 8. LoRA 论文阅读

### 论文信息

```
标题：LoRA: Low-Rank Adaptation of Large Language Models
作者：Edward Hu 等（微软研究院）
链接：https://arxiv.org/abs/2106.09685
```

### 核心问题

```
大模型微调太贵了！
├── GPT-3 有 1750 亿参数
├── 全参数微调需要更新所有参数
├── GPU 内存需要 1.2TB
└── 每个任务都要重新训练一次
```

### 解决方案

```
LoRA = Low-Rank Adaptation（低秩适配）

核心思想：
├── 冻结原模型参数（不动）
├── 注入小的可训练矩阵（只训练这个）
└── 效果接近全参数微调
```

### 关键数据

```
对于 GPT-3 175B：
├── 参数量：减少 10000 倍
├── GPU 内存：减少 2/3
├── 检查点大小：减少 10000 倍
└── 推理时没有额外延迟
```

### 技术原理（简化版）

```
原模型权重：W（不动）
新增权重：ΔW = A × B（只训练这个）
推理时：W + A × B
```

### 实用建议

```
├── 微调 Wq 和 Wv 效果最好
├── 秩 r = 4 或 8 就够用
└── 推理时没有额外延迟
```

### 为什么推理时没有额外延迟？

```
推理时：
├── 把 A × B 合并到 W 里
├── 得到 W' = W + A × B
├── 和全参数微调的模型一样
└── 所以没有额外计算
```

---

## 9. 学习心得

### 今天学到了什么？
- 微调 vs Prompt Engineering 的区别
- LoRA：低成本、效果好的微调方法
- Hugging Face：大模型托管平台
- 微调流程：下载模型 → 准备数据 → LoRA 训练 → 测试 → 部署
- LoRA 原理：用小矩阵近似大矩阵，只训练小部分参数
- 常用工具：Hugging Face Transformers、PEFT、LLaMA-Factory
- 论文阅读：理解 LoRA 的核心思想和关键数据

### 遇到的问题？
- 微调步骤、工具选用还不清楚（现在清楚了）
- 底层原理一知半解（现在理解了低秩适配的原理）

### 明天要学什么？
- 文本切分策略

---

*最后更新：2026年7月4日*
