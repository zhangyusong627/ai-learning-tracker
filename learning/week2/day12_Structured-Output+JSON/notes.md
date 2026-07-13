# Day 12 - Structured Output + 稳定 JSON

## 学习时间
2026年6月10日

## 学习目标
- 理解 Structured Output 的概念和作用
- 理解 JSON 格式和用途
- 掌握让 AI 输出稳定 JSON 的方法
- 了解 Temperature 对输出稳定性的影响

---

## 一、为什么需要 Structured Output？

**问题**：AI 输出的格式不稳定

```
用户：请列出 3 个编程语言
AI：Python、Java、JavaScript

用户：请用 JSON 格式列出 3 个编程语言
AI：{"languages": ["Python", "Java", "JavaScript"]}

用户：请用 JSON 格式列出 3 个编程语言
AI：{"languages": ["Python", "Java", "Go"]}  // 每次不一样！
```

**需求**：让 AI 输出固定格式的数据，便于程序处理。

---

## 二、什么是 Structured Output？

**一句话**：让 AI 按照指定的格式输出数据。

### Java 类比

```java
// 定义接口
public class LanguageResponse {
    private List<String> languages;
    private String count;
}

// AI 输出必须符合这个格式
{
    "languages": ["Python", "Java", "JavaScript"],
    "count": "3"
}
```

---

### Structured Output 的价值

| 价值 | 说明 |
|------|------|
| **程序易解析** | 可以直接被程序读取和处理 |
| **格式稳定** | 每次输出格式一致 |
| **便于集成** | 可以直接存入数据库或调用 API |
| **减少错误** | 避免格式不一致导致的解析错误 |

---

## 三、JSON 是什么？

**JSON = JavaScript Object Notation**（JavaScript 对象表示法）

```
{
    "name": "张三",
    "age": 25,
    "skills": ["Java", "Python", "AI"]
}
```

---

### 为什么用 JSON？

| 原因 | 说明 |
|------|------|
| **程序容易解析** | 所有语言都有 JSON 解析库 |
| **跨语言通用** | Java、Python、Go、JavaScript 都支持 |
| **结构清晰** | 键值对格式，易于理解 |
| **标准规范** | 有标准的 JSON Schema 验证 |

---

### JSON 的基本语法

```json
// 对象
{
    "key": "value"
}

// 数组
{
    "languages": ["Python", "Java", "JavaScript"]
}

// 嵌套
{
    "user": {
        "name": "张三",
        "skills": ["Java", "AI"]
    }
}
```

---

## 四、怎么让 AI 输出稳定的 JSON？

### 方法 1：在 Prompt 中明确指定

```
请用 JSON 格式输出 3 个编程语言，格式如下：
{
    "languages": ["语言1", "语言2", "语言3"]
}
```

**问题**：AI 可能输出格式不一致

---

### 方法 2：给 JSON 示例

```
请用 JSON 格式输出编程语言。

示例：
{
    "languages": ["Python", "Java", "JavaScript"]
}

现在请输出 3 个前端框架：
```

**效果更好，但仍然可能有变化。**

---

### 方法 3：使用 JSON Schema（最可靠）

```
请按照以下 JSON Schema 输出：

{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "languages": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["languages"]
}

输出 3 个编程语言：
```

**效果**：AI 输出一定符合 Schema

---

### 三种方法对比

| 方法 | 效果 | 推荐度 |
|------|------|--------|
| 明确指定格式 | 一般 | ⭐⭐ |
| 给 JSON 示例 | 较好 | ⭐⭐⭐ |
| 使用 JSON Schema | 最好 | ⭐⭐⭐⭐⭐ |

---

## 五、Java 代码示例

### 1. 定义数据结构

```java
public class LanguageResponse {
    private List<String> languages;

    // getters and setters
    public List<String> getLanguages() { return languages; }
    public void setLanguages(List<String> languages) { this.languages = languages; }
}
```

### 2. 调用 AI 并解析

```java
public class StructuredOutputExample {

    public static void main(String[] args) {
        // 1. 构造 Prompt
        String prompt = """
            请用 JSON 格式输出 3 个编程语言，格式如下：
            {"languages": ["语言1", "语言2", "语言3"]}
            """;

        // 2. 调用 AI
        String aiResponse = callAI(prompt);

        // 3. 解析 JSON
        ObjectMapper mapper = new ObjectMapper();
        try {
            LanguageResponse response = mapper.readValue(aiResponse, LanguageResponse.class);
            System.out.println("AI 输出的语言: " + response.getLanguages());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static String callAI(String prompt) {
        // 调用 AI API
        return "{\"languages\": [\"Python\", \"Java\", \"JavaScript\"]}";
    }
}
```

### 3. 完整的 JSON 处理工具类

```java
public class JsonUtils {

    private static final ObjectMapper mapper = new ObjectMapper();

    // 解析 JSON
    public static <T> T parseJson(String json, Class<T> clazz) {
        try {
            return mapper.readValue(json, clazz);
        } catch (Exception e) {
            throw new RuntimeException("JSON 解析失败: " + e.getMessage());
        }
    }

    // 验证 JSON 格式
    public static boolean isValidJson(String json) {
        try {
            mapper.readTree(json);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    // 格式化 JSON
    public static String formatJson(String json) {
        try {
            Object obj = mapper.readValue(json, Object.class);
            return mapper.writerWithDefaultPrettyPrinter().writeValueAsString(obj);
        } catch (Exception e) {
            return json;
        }
    }
}
```

---

## 六、JSON 输出不稳定的原因

| 原因 | 说明 |
|------|------|
| **温度（Temperature）** | 高温度会导致随机性增加 |
| **Token 限制** | 可能输出被截断 |
| **格式理解偏差** | AI 可能理解错格式要求 |
| **模型能力** | 小模型更难输出稳定格式 |

---

## 七、如何让 JSON 更稳定？

### 1. 降低温度

```
Temperature: 0.0  // 最稳定，但可能缺乏创造性
Temperature: 0.3  // 推荐值，平衡稳定性和创造性
Temperature: 1.0  // 最有创造性，但不稳定
```

### 2. 明确格式要求

```
请严格按照以下 JSON 格式输出，不要添加任何其他内容：
{"languages": ["Python", "Java", "JavaScript"]}
```

### 3. 使用 Schema 验证

```java
// 验证 AI 输出是否符合 Schema
public boolean validateJsonSchema(String json, String schema) {
    // 使用 JSON Schema 验证库
    JsonSchemaFactory factory = JsonSchemaFactory.getInstance();
    JsonSchema jsonSchema = factory.getSchema(schema);
    JsonNode node = objectMapper.readTree(json);
    return jsonSchema.validate(node).isSuccess();
}
```

### 4. 重试机制

```java
public String getStableJsonOutput(String prompt, String schema, int maxRetries) {
    for (int i = 0; i < maxRetries; i++) {
        String output = callAI(prompt);
        if (validateJsonSchema(output, schema)) {
            return output;
        }
    }
    throw new RuntimeException("无法生成稳定的 JSON 输出");
}
```

### 5. 后处理修复

```java
public String fixJson(String output) {
    // 1. 移除多余的空白字符
    output = output.trim();

    // 2. 移除多余的逗号
    output = output.replaceAll(",\\s*}", "}");
    output = output.replaceAll(",\\s*]", "]");

    // 3. 添加缺失的引号
    // （这里需要更复杂的逻辑，实际项目中建议使用 JSON 解析库）

    return output;
}
```

---

## 八、Temperature 详解

### 什么是 Temperature？

**Temperature = 控制 AI 输出随机性的参数**

| 值 | 效果 | 适用场景 |
|------|------|----------|
| **0.0** | 最稳定，每次输出几乎一样 | 数据提取、格式化输出 |
| **0.3** | 稳定，略有变化 | 一般任务 |
| **0.7** | 平衡，有创造性 | 创意写作 |
| **1.0** | 最随机，每次输出不同 | 头脑风暴、创意生成 |

---

### Java 代码示例

```java
public class TemperatureExample {

    public static void main(String[] args) {
        // 低温度：稳定输出
        String stable = callAI("列出 3 个编程语言", 0.0);
        // 每次都是：["Python", "Java", "JavaScript"]

        // 高温度：随机输出
        String random = callAI("列出 3 个编程语言", 1.0);
        // 每次可能不同：["Python", "Go", "Rust"]
    }

    private static String callAI(String prompt, double temperature) {
        // 调用 AI API，传入 temperature 参数
        return "AI 输出";
    }
}
```

---

## 九、实际应用场景

### 1. 数据提取

```
Prompt：从以下文本中提取姓名、年龄、地址，用 JSON 格式输出：
"张三，25 岁，住在北京市朝阳区"

输出：
{
    "name": "张三",
    "age": 25,
    "address": "北京市朝阳区"
}
```

### 2. API 集成

```java
// AI 输出可以直接调用 API
String aiOutput = "{\"action\": \"sendEmail\", \"to\": \"test@example.com\"}";
EmailRequest request = parseJson(aiOutput, EmailRequest.class);
emailService.send(request);
```

### 3. 数据库存储

```java
// AI 输出可以直接存入数据库
String aiOutput = "{\"name\": \"张三\", \"score\": 95}";
Student student = parseJson(aiOutput, Student.class);
studentRepository.save(student);
```

### 4. 前端展示

```javascript
// AI 输出可以直接渲染到页面
const aiOutput = '{"name": "张三", "skills": ["Java", "AI"]}';
const data = JSON.parse(aiOutput);
document.getElementById('name').innerText = data.name;
```

---

## 十、Structured Output vs 自由文本

| 维度 | Structured Output | 自由文本 |
|------|-------------------|----------|
| **格式** | 固定格式（JSON） | 不固定 |
| **解析** | 程序容易解析 | 需要额外处理 |
| **稳定性** | 稳定 | 不稳定 |
| **适用场景** | 程序处理 | 人类阅读 |
| **Token 消耗** | 可能更多 | 更少 |
| **创造性** | 较低 | 较高 |

---

## 十一、核心思想总结

| 概念 | 一句话解释 |
|------|------------|
| **Structured Output** | 让 AI 按固定格式输出 |
| **JSON** | JavaScript Object Notation，通用数据格式 |
| **JSON Schema** | 定义 JSON 结构的规范 |
| **Temperature** | 控制输出随机性的参数 |
| **重试机制** | 输出不符合格式时重新生成 |
| **后处理** | 修复 AI 输出的格式问题 |

---

## 十二、练习题

### 题目 1：Structured Output 的定义

请用一句话解释什么是 Structured Output。

**答案**：Structured Output 是让 AI 按照指定的格式输出数据，便于程序处理。

---

### 题目 2：JSON 的含义

JSON 是什么的缩写？全称是什么？

**答案**：JSON = JavaScript Object Notation（JavaScript 对象表示法）

---

### 题目 3：让 JSON 稳定的方法

请列出 3 种让 AI 输出稳定 JSON 的方法。

**答案**：
1. 在 Prompt 中明确指定格式
2. 给 JSON 示例
3. 使用 JSON Schema

---

### 题目 4：Temperature 的作用

Temperature 设为 0 意味着什么？

**答案**：Temperature = 0 意味着 AI 输出最稳定，每次输出几乎一样，但可能缺乏创造性。

---

### 题目 5：Java 实现

用 Java 写一个方法，验证 JSON 字符串是否有效。

**答案**：
```java
public static boolean isValidJson(String json) {
    try {
        ObjectMapper mapper = new ObjectMapper();
        mapper.readTree(json);
        return true;
    } catch (Exception e) {
        return false;
    }
}
```

---

### 题目 6：重试机制

如果 AI 输出的 JSON 不符合格式，应该怎么处理？

**答案**：使用重试机制，重新生成 JSON，直到符合格式要求或达到最大重试次数。

---

### 题目 7：应用场景

Structured Output 有哪些实际应用场景？

**答案**：
1. 数据提取：从文本中提取结构化数据
2. API 集成：AI 输出可以直接调用 API
3. 数据库存储：AI 输出可以直接存入数据库
4. 前端展示：AI 输出可以直接渲染到页面

---

### 题目 8：对比分析

Structured Output 和自由文本各有什么优缺点？

**答案**：
- Structured Output：格式稳定、程序易解析、便于集成，但创造性较低
- 自由文本：格式灵活、创造性高，但格式不稳定、程序难解析

---

## 十三、学习心得

- Structured Output 是让 AI 按固定格式输出，便于程序处理
- JSON = JavaScript Object Notation，是通用的数据格式
- 让 JSON 稳定的方法：明确格式、给示例、使用 Schema、降低温度、重试机制
- Temperature 控制输出随机性，0 最稳定，1.0 最随机
- 实际应用中，Structured Output 非常重要，可以让 AI 输出直接被程序使用
- 后处理可以修复一些格式问题，但最好让 AI 直接输出正确格式
- Structured Output 适合程序处理，自由文本适合人类阅读

---

## 十四、待复习内容

- [ ] Structured Output 的概念和作用
- [ ] JSON 的基本语法和用途
- [ ] 让 AI 输出稳定 JSON 的方法
- [ ] Temperature 对输出稳定性的影响
- [ ] Java 中处理 JSON 的常用库
- [ ] 重试机制和后处理修复

---

## 十五、下一步学习

- [ ] Day 13：幻觉控制+Temperature+System Prompt
- [ ] 学习如何控制 AI 的幻觉问题

---

*笔记创建时间：2026年6月10日*
*学习时长：1.5小时*
*掌握程度：★★★★☆*