# LoRA 论文

## 论文信息

```
标题：LoRA: Low-Rank Adaptation of Large Language Models
作者：Edward J. Hu 等（微软研究院）
发表时间：2021年6月
```

## 下载链接

- **arXiv 页面**：https://arxiv.org/abs/2106.09685
- **PDF 直接下载**：https://arxiv.org/pdf/2106.09685

## 论文核心内容

### 问题
全参数微调大模型成本太高（GPT-3 1750亿参数）

### 解决方案
LoRA：冻结原模型，只训练小矩阵

### 关键数据
- 参数量：减少 10000 倍
- GPU 内存：减少 3 倍
- 效果：接近全参数微调

### 技术原理
```
原模型权重：W（不动）
新增权重：ΔW = A × B（只训练这个）
推理时：W + A × B
```

### 实用建议
- 微调 Attention 层（Q、V 效果最好）
- 秩 r = 4 或 8 就够用
- 推理时没有额外延迟

## 相关资源

- **Hugging Face PEFT**：https://huggingface.co/docs/peft
- **LLaMA-Factory**：https://github.com/hiyouga/LLaMA-Factory
