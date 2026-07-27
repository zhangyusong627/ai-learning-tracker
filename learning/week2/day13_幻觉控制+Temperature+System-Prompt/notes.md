# Day 13 - 幻觉控制 + Temperature + System Prompt

## 学习时间
2026年6月10日

## 学习目标
- 理解 AI 幻觉的概念和危害
- 掌握控制幻觉的方法
- 深入理解 System Prompt 的专业原理
- 深入理解 Temperature 的数学原理

---

## 一、什么是 AI 幻觉？

**一句话**：AI 自信地说假话，但自己不知道是假的。

---

### 例子

```
用户：2026 年诺贝尔物理学奖得主是谁？
AI：2026 年诺贝尔物理学奖得主是张三。
```

**问题**：
- 2026 年还没结束
- AI 不知道谁得奖
- 但它编了一个答案，还很自信

---

### 为什么会产生幻觉？

| 原因 | 说明 |
|------|------|
| **训练数据** | 数据有截止日期，之后的事不知道 |
| **概率生成** | AI 是预测下一个词，不是查数据库 |
| **缺乏常识** | 不知道什么是"不知道" |
| **过度自信** | 会编造看起来合理的答案 |

---

### 幻觉的危害

| 场景 | 危害 |
|------|------|
| **医疗** | AI 给出错误的诊断建议 |
| **法律** | AI 引用不存在的判例 |
| **金融** | AI 给出错误的投资建议 |
| **新闻** | AI 编造虚假信息 |

---

## 二、如何控制幻觉？

### 方法 1：明确告知不知道就说不知道

```
System Prompt:
你是问答助手。如果不确定答案，请说"我不确定"，不要编造答案。
```

**效果**：AI 更可能说"我不知道"

---

### 方法 2：要求引用来源

```
请回答以下问题，并注明信息来源：
2026 年诺贝尔物理学奖得主是谁？
```

**效果**：AI 会说"我没有相关信息"

---

### 方法 3：限制回答范围

```
System Prompt:
你只能回答以下领域的问题：Java 编程、Python 编程、AI 基础。
对于其他领域的问题，请说"这个问题超出了我的知识范围"。
```

**效果**：减少超出能力范围的回答

---

### 方法 4：使用 CoT 让 AI 展示推理过程

```
请一步步思考这个问题，如果你不确定，请说明哪些部分是确定的，哪些是不确定的：
2026 年诺贝尔物理学奖得主是谁？
```

**效果**：AI 会暴露自己的不确定性

---

## 三、Temperature 与幻觉的关系

| Temperature | 幻觉风险 | 原因 |
|-------------|----------|------|
| **0.0** | 低 | 输出最稳定，不容易编造 |
| **0.3** | 较低 | 平衡稳定性和创造性 |
| **0.7** | 中等 | 有一定随机性 |
| **1.0** | 高 | 最随机，容易编造 |

**建议**：对于需要准确性的任务，使用低温度。

---

## 四、System Prompt 控制幻觉

### 完整示例

```
System Prompt:
你是问答助手，负责回答用户的问题。

重要规则：
1. 如果不确定答案，请说"我不确定，请核实相关信息"
2. 不要编造答案，即使看起来很合理
3. 对于事实性问题，请注明信息来源或说"我没有相关信息"
4. 对于观点性问题，请说明"这是我的理解，仅供参考"
5. 如果问题超出你的知识范围，请说"这个问题超出了我的知识范围"

你的目标是提供准确、有用的信息，而不是给出所有问题的答案。
```

---

### 分场景控制

#### 场景 1：医疗咨询

```
System Prompt:
你是医疗健康助手，但你不是医生。

规则：
1. 你只能提供一般性的健康信息
2. 不要给出诊断或治疗建议
3. 对于具体症状，请说"建议咨询专业医生"
4. 不要推荐具体药物
```

#### 场景 2：法律咨询

```
System Prompt:
你是法律知识助手，但你不是律师。

规则：
1. 你只能解释法律条文的一般含义
2. 不要给出法律意见
3. 对于具体案件，请说"建议咨询专业律师"
4. 不要引用不存在的判例
```

#### 场景 3：金融建议

```
System Prompt:
你是金融知识助手，但你不是理财顾问。

规则：
1. 你只能解释金融概念
2. 不要给出投资建议
3. 对于具体投资决策，请说"建议咨询专业理财顾问"
4. 不要预测市场走势
```

---

## 五、深入讨论：System Prompt 专业解析

### 定义

**System Prompt = 预设的系统级指令**，用于定义 AI 的行为边界、角色定位和响应规则。

在技术实现上，System Prompt 是 API 请求中的一个特殊参数：

```json
{
    "model": "gpt-4",
    "messages": [
        {"role": "system", "content": "你是翻译专家..."},
        {"role": "user", "content": "请翻译：Hello World"}
    ]
}
```

---

### 技术原理

#### 1. 消息角色（Message Roles）

| 角色 | 作用 | 优先级 |
|------|------|--------|
| **system** | 定义 AI 行为，全局生效 | 最高 |
| **user** | 用户输入 | 中 |
| **assistant** | AI 的回复 | 低 |

**优先级**：system > user > assistant

#### 2. 注意力机制中的位置

```
System Prompt → 最先被处理，影响后续所有生成
     ↓
User Input → 在 System Prompt 的约束下处理
     ↓
AI Output → 在前两者的约束下生成
```

**类比**：System Prompt 像是"宪法"，User Input 是"具体案件"，AI Output 是"判决结果"。

---

### System Prompt 的技术层级

#### 层级 1：角色定义（Role Definition）

```
你是[角色]，专注于[领域]。
```

**技术作用**：激活模型在特定领域的知识分布。

#### 层级 2：行为约束（Behavioral Constraints）

```
规则：
1. 只回答[领域]相关的问题
2. 不执行[禁止行为]
```

**技术作用**：限制模型的输出空间，减少幻觉和越界。

#### 层级 3：输出格式（Output Formatting）

```
输出格式：
- 使用 Markdown
- 包含标题和列表
```

**技术作用**：控制解码过程，确保输出可被程序解析。

#### 层级 4：异常处理（Exception Handling）

```
如果遇到[情况]，请[处理方式]
```

**技术作用**：覆盖边缘情况，提高鲁棒性。

---

### System Prompt 的最佳实践

#### 1. 明确性原则

```
❌ 模糊：你是专家
✅ 明确：你是资深 Java 架构师，专注于分布式系统设计
```

#### 2. 边界清晰原则

```
❌ 模糊：不要做不该做的事
✅ 明确：不要给出医疗诊断、法律意见、投资建议
```

#### 3. 分层结构原则

```
System Prompt 结构：
1. 角色定义（1-2 句）
2. 核心能力（3-5 条）
3. 行为规则（5-10 条）
4. 输出格式（1-3 条）
5. 异常处理（2-3 条）
```

#### 4. 示例引导原则

```
示例：
用户：你好
AI：你好！我是翻译专家，请问需要翻译什么内容？
```

---

### System Prompt 的高级用法

#### 1. 多轮对话管理

```
System Prompt:
对话历史会存储在 messages 中。
你需要基于完整对话历史回答，不要重复已说过的内容。
```

#### 2. 知识注入

```
System Prompt:
以下是你的知识库：
{知识库内容}

请基于以上知识回答问题，不要编造信息。
```

#### 3. 动态 System Prompt

```java
// 根据用户权限动态生成 System Prompt
String systemPrompt = String.format("""
    你是助手。
    用户权限：%s
    根据权限，用户可以：%s
    """, userPermission, getAccessibleFeatures(userPermission));
```

---

## 六、深入讨论：Temperature 专业解析

### 定义

**Temperature = 控制输出随机性的采样参数**，范围通常为 0.0 到 2.0。

---

### 数学原理

#### 1. 原始输出（Logits）

AI 输出的是每个词的原始分数（logits）：

```
"今天"：2.5
"明天"：1.8
"昨天"：0.9
```

#### 2. 温度缩放（Temperature Scaling）

```
scaled_logit = logit / temperature
```

| Temperature | 效果 |
|-------------|------|
| **0.5** | 分数差距放大，最高分更突出 |
| **1.0** | 原始分数，不变 |
| **2.0** | 分数差距缩小，更均匀 |

#### 3. 概率分布（Softmax）

```
P(word) = exp(scaled_logit) / Σexp(scaled_logits)
```

**直观理解**：

```
Temperature = 0.5：
"今天"：70%  →  95%
"明天"：20%  →   4%
"昨天"：10%  →   1%

Temperature = 2.0：
"今天"：70%  →  45%
"明天"：20%  →  30%
"昨天"：10%  →  25%
```

---

### Temperature 的技术影响

#### 1. 输出多样性（Diversity）

| Temperature | 多样性 | 适用场景 |
|-------------|--------|----------|
| **0.0** | 最低 | 数据提取、格式化输出 |
| **0.3** | 低 | 一般任务、问答 |
| **0.7** | 中 | 创意写作、头脑风暴 |
| **1.0** | 高 | 高创造性任务 |
| **>1.0** | 最高 | 实验性任务 |

#### 2. 输出质量（Quality）

```
Temperature 过低：
- 输出重复、单调
- 缺乏创造性
- 可能陷入局部最优

Temperature 过高：
- 输出混乱、不连贯
- 可能生成无意义内容
- 幻觉风险增加
```

#### 3. 与任务的匹配

| 任务类型 | 推荐 Temperature | 原因 |
|----------|------------------|------|
| **数据提取** | 0.0 - 0.2 | 需要确定性 |
| **问答** | 0.3 - 0.5 | 平衡准确性和自然度 |
| **翻译** | 0.3 - 0.5 | 需要准确，但也要自然 |
| **创意写作** | 0.7 - 1.0 | 需要创造性 |
| **代码生成** | 0.0 - 0.3 | 需要准确性 |

---

### Temperature 与其他参数的关系

#### 1. Top-p（核采样）

```
Top-p = 0.9 → 只从累计概率达到 90% 的词中采样
```

**与 Temperature 的关系**：
- Temperature 控制概率分布的形状
- Top-p 控制采样范围

**推荐**：通常只调一个，不要同时调。

#### 2. Top-k

```
Top-k = 50 → 只从概率最高的 50 个词中采样
```

**与 Temperature 的关系**：
- Temperature 影响所有词的概率
- Top-k 限制候选词数量

#### 3. Frequency Penalty / Presence Penalty

```
Frequency Penalty = 2.0 → 重复的词概率降低
Presence Penalty = 1.0 → 出现过的词概率降低
```

**作用**：减少重复，增加多样性。

---

### Temperature 的技术实现

```python
import torch
import torch.nn.functional as F

def sample_with_temperature(logits, temperature=1.0):
    """
    使用 Temperature 采样

    Args:
        logits: 模型输出的原始分数
        temperature: 温度参数

    Returns:
        采样得到的 token
    """
    # 温度缩放
    scaled_logits = logits / temperature

    # 转换为概率分布
    probabilities = F.softmax(scaled_logits, dim=-1)

    # 采样
    token = torch.multinomial(probabilities, num_samples=1)

    return token
```

---

### Temperature 的最佳实践

#### 1. 根据任务选择

```
确定性任务（数据提取、格式化）：Temperature = 0.0
准确性任务（问答、翻译）：Temperature = 0.3 - 0.5
创造性任务（写作、创意）：Temperature = 0.7 - 1.0
```

#### 2. 先低后高

```
先用低 Temperature 测试基本功能
确认基本功能正确后，再提高 Temperature 增加创造性
```

#### 3. 组合使用

```
Temperature + Top-p：
Temperature = 0.7（中等创造性）
Top-p = 0.9（限制采样范围）
```

#### 4. 实验调优

```
不同任务需要不同的 Temperature
建议：先用默认值，根据输出效果调整
```

---

## 七、System Prompt 与 Temperature 的协同

### 组合策略

| 场景 | System Prompt | Temperature |
|------|---------------|-------------|
| **数据提取** | 明确格式要求 | 0.0 |
| **问答** | 要求准确回答 | 0.3 |
| **创意写作** | 鼓励创造性 | 0.7 |
| **代码生成** | 要求可执行代码 | 0.0 - 0.3 |

### 示例

**场景：客服机器人**

```
System Prompt:
你是客服机器人，专注于产品咨询。
规则：
1. 只回答产品相关问题
2. 不确定时说"建议联系人工客服"
3. 语气友好、专业

Temperature: 0.3
```

**效果**：回答准确、稳定，同时保持自然。

---

## 八、Java 代码示例

```java
public class HallucinationControl {

    // 构造防幻觉的 System Prompt
    public static String buildSafeSystemPrompt(String domain) {
        return String.format("""
            你是%s助手。

            重要规则：
            1. 如果不确定答案，请说"我不确定"
            2. 不要编造答案
            3. 对于事实性问题，请注明信息来源
            4. 如果问题超出你的知识范围，请说"这个问题超出了我的知识范围"

            你的目标是提供准确、有用的信息。
            """, domain);
    }

    // 检测可能的幻觉
    public static boolean mightBeHallucination(String response) {
        // 检查是否包含过度自信的表述
        String[] confidentPhrases = {"绝对是", "肯定是", "100%", "毫无疑问"};
        for (String phrase : confidentPhrases) {
            if (response.contains(phrase)) {
                return true;  // 可能是幻觉
            }
        }
        return false;
    }

    // 处理 AI 输出
    public static String processResponse(String response) {
        if (mightBeHallucination(response)) {
            return "注意：AI 的回答可能不够准确，请核实相关信息。\\n\\n" + response;
        }
        return response;
    }
}
```

---

## 九、幻觉检测方法

| 方法 | 说明 | 准确度 |
|------|------|--------|
| **自我检测** | 让 AI 自己检查是否确定 | 中等 |
| **多模型验证** | 用多个模型回答同一问题 | 较高 |
| **知识库对比** | 与权威知识库对比 | 高 |
| **人工审核** | 人工检查关键信息 | 最高 |

---

## 十、最佳实践清单

| 实践 | 优先级 |
|------|--------|
| **System Prompt 明确规则** | ⭐⭐⭐ |
| **要求引用来源** | ⭐⭐⭐ |
| **限制回答范围** | ⭐⭐⭐ |
| **使用低温度** | ⭐⭐⭐ |
| **要求展示推理过程** | ⭐⭐ |
| **多模型验证** | ⭐⭐ |
| **人工审核关键信息** | ⭐⭐⭐ |

---

## 十一、核心思想总结

| 概念 | 一句话解释 |
|------|------------|
| **AI 幻觉** | AI 自信地说假话，但自己不知道是假的 |
| **幻觉原因** | 概率生成、缺乏"不知道"的概念 |
| **控制方法** | System Prompt 明确规则、要求引用来源、限制回答范围 |
| **System Prompt** | 预设的系统级指令，定义 AI 的行为边界 |
| **Temperature** | 控制输出随机性的采样参数 |
| **Temperature Scaling** | scaled_logit = logit / temperature |
| **Top-p** | 核采样，限制采样范围 |

---

## 十二、练习题

### 题目 1：AI 幻觉

请用一句话解释什么是 AI 幻觉。

**答案**：AI 幻觉是 AI 自信地说假话，但自己不知道是假的。

---

### 题目 2：幻觉原因

为什么 AI 会产生幻觉？

**答案**：
1. 训练数据有截止日期
2. AI 是概率生成，不是查数据库
3. 缺乏"不知道"的概念
4. 会编造看起来合理的答案

---

### 题目 3：控制方法

如何控制 AI 幻觉？请列出 3 种方法。

**答案**：
1. 明确告知不知道就说不知道
2. 要求引用来源
3. 限制回答范围

---

### 题目 4：Temperature 与幻觉

Temperature 与幻觉的关系是什么？

**答案**：Temperature 越高，幻觉风险越高；Temperature 越低，幻觉风险越低。

---

### 题目 5：System Prompt 定义

System Prompt 是什么？

**答案**：System Prompt 是预设的系统级指令，用于定义 AI 的行为边界、角色定位和响应规则。

---

### 题目 6：消息角色优先级

在 API 请求中，system、user、assistant 三个角色的优先级是什么？

**答案**：system > user > assistant

---

### 题目 7：Temperature 数学原理

Temperature 的数学原理是什么？

**答案**：scaled_logit = logit / temperature，通过温度缩放改变概率分布。

---

### 题目 8：System Prompt 最佳实践

System Prompt 的最佳实践是什么？

**答案**：
1. 明确性原则：明确定义角色和能力
2. 边界清晰原则：明确不能做什么
3. 分层结构原则：按层级组织内容
4. 示例引导原则：提供示例

---

## 十三、学习心得

- AI 幻觉是 AI 自信地说假话，自己不知道是假的
- 控制幻觉需要 System Prompt 明确规则、要求引用来源、限制回答范围
- Temperature 越低，幻觉风险越低
- System Prompt 是预设的系统级指令，优先级最高
- System Prompt 的技术层级：角色定义、行为约束、输出格式、异常处理
- Temperature 的数学原理：scaled_logit = logit / temperature
- Top-p 控制采样范围，与 Temperature 配合使用
- 不同任务需要不同的 Temperature 设置
- System Prompt 与 Temperature 需要协同使用

---

## 十四、待复习内容

- [ ] AI 幻觉的概念和危害
- [ ] 控制幻觉的方法
- [ ] System Prompt 的专业原理
- [ ] Temperature 的数学原理
- [ ] System Prompt 的最佳实践
- [ ] Temperature 与其他参数的关系

---

## 十五、下一步学习

- [ ] Day 14：Prompt 库整理+项目集成
- [ ] 整理所有 Prompt 模板，形成个人知识库

---

*笔记创建时间：2026年6月10日*
*学习时长：2小时*
*掌握程度：★★★★☆*