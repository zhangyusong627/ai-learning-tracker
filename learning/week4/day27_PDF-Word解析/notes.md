# Day 27：PDF/Word 解析与批量处理

## 学习时间

2026年7月13日

## 学习目标

- 理解“读取文件”和“解析文档”的区别
- 使用 PyMuPDF 解析电子文本型 PDF
- 使用 python-docx 解析 Word 段落和表格
- 保留 Word 中段落与表格的原始顺序
- 统一输出为 LangChain `Document`
- 批量处理目录中的 PDF 和 Word
- 接入文本切分，并保留来源元数据

---

## 一、读取文件与解析文档

### 读取文件

IO 只负责获取文件中的原始字节或字符，不理解这些数据表示页面、段落还是表格。

### 解析文档

解析器按照 PDF、Word 的格式规范理解文档结构，并提取文字、页面、段落和表格。

```text
读取文件：拿到原始数据
文档解析：理解格式并提取结构化内容
OCR：识别图片中的文字
```

### 电子 PDF 与扫描 PDF

- 电子文本型 PDF：存在文本层，可以使用 `page.get_text()`。
- 扫描型 PDF：页面主要是图片，普通解析器通常提取不到文字，需要 OCR。
- `get_text()` 返回空字符串只能说明没有提取到文本，不能直接断定页面一定需要 OCR，也可能是空白页。

---

## 二、PDF 解析

使用 PyMuPDF：

```python
import fitz
```

核心流程：

```text
PDF 路径
→ fitz.open()
→ Document
→ Page
→ page.get_text()
→ LangChain Document
```

PDF 按页解析，因为 PDF 的页面边界是固定的。每页保存：

```python
{
    "source": "2106.09685v2.pdf",
    "file_type": "pdf",
    "page": 1,
}
```

使用 `with fitz.open(...)` 后不再手动调用 `close()`，否则会重复关闭并触发：

```text
ValueError: document closed
```

测试结果：

```text
PDF 总页数：26
成功提取页面：26
未提取页面：0
```

PDF 文本提取仍可能包含版面噪声，例如单词被换行和连字符拆开：

```text
LAN-
GUAGE
```

---

## 三、Word 解析

使用 python-docx：

```python
from docx import Document
```

Word 的普通内容分为不同集合：

```text
Word Document
├── paragraphs：标题和普通段落
└── tables：表格
```

标题也是段落，只是样式不同：

```text
Heading 1
Heading 2
Normal
```

### 为什么不能先遍历 paragraphs，再遍历 tables？

这种写法会破坏表格和段落的原始相对顺序。解决办法是遍历 Word 底层 XML：

```text
p      → Paragraph
tbl    → Table
sectPr → 页面设置，忽略
```

最终保留了：

```text
服务明细
→ 服务价格表格
→ 补充说明
```

Word 按逻辑内容块解析，不保存可靠页码。Word 页码会受到字体、页边距、纸张大小和排版引擎影响。

测试结果：

```text
Word 内容块：7
├── 段落：6
└── 表格：1
```

表格作为一个完整语义单元保存，避免表头和数据行分离。

---

## 四、统一 LangChain Document

PDF 和 Word 最终都转换为：

```python
LangChainDocument(
    page_content="正文",
    metadata={...},
)
```

职责划分：

```text
page_content → 保存正文和语义
metadata     → 保存来源、位置、类型和追踪信息
```

元数据不会自动提高向量相似度，但可以用于：

- 引用来源和页码
- 定位原文与排查错误
- 按文件、部门和权限过滤
- 文档更新时删除旧向量
- 管理文档版本

---

## 五、批量文档加载器

最终数据流：

```text
documents/
    ↓
load_directory()
    ↓
load_document()
    ↓
┌───────────────┬───────────────┐
│ load_pdf()    │ load_word()   │
└───────────────┴───────────────┘
    ↓
list[LangChainDocument]
```

### 解析器注册表

```python
DOCUMENT_LOADERS = {
    ".pdf": load_pdf,
    ".docx": load_word,
}
```

注册表保存的是函数引用，不是函数执行结果：

```text
load_pdf            → 函数本身，稍后执行
load_pdf(file_path) → 立即执行函数
```

字典 Key 唯一；给同一个 Key 再赋值会更新原 Value。Java 类比为 `Map.put()`。

### append 与 extend

```text
append(list) → 把整个列表作为一个元素加入，形成嵌套列表
extend(list) → 把列表中的元素逐个加入，得到扁平列表
```

批量合并文档使用：

```python
all_documents.extend(file_documents)
```

### 批处理状态

```text
success_files：格式受支持，且成功提取到内容
failed_files：格式受支持，但解析过程中抛出异常
skipped_files：当前不支持该文件格式
empty_files：解析没有报错，但未提取到文字
```

异常按单个文件隔离；一个文件失败不会清空之前成功解析的结果，也不会阻止后续文件继续处理。

---

## 六、接入文本切分

使用：

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
```

当前 LangChain 已将文本切分器拆成独立包，旧导入路径 `langchain.text_splitter` 不适用于当前环境。

参数：

```python
chunk_size=500
chunk_overlap=100
```

运行结果：

```text
切分前 Document：33
├── PDF 页面：26
└── Word 内容块：7

切分后 Chunk：227
```

文本切分的目的：

- 提高语义检索粒度
- 减少无关上下文和 Token 成本
- 避免长文本压缩到固定维度向量后产生语义稀释
- 通过重叠窗口减少切分点的信息丢失

切分后的 Chunk 会继承原 `Document` 的元数据，从而保持来源可追踪。

---

## 七、项目文件

```text
day27_PDF-Word解析/
├── documents/              # 批量处理测试输入
├── create_sample_docx.py   # 创建 Word 测试文档
├── pdf_parser.py           # PDF 分步练习
├── word_parser.py          # Word 基础解析练习
├── word_order_parser.py    # Word 保序解析练习
├── document_loader.py      # 最终批量文档加载器
└── notes.md                # 本笔记
```

---

## 八、当前实现边界

暂未实现：

- 扫描 PDF OCR
- PDF 表格结构识别
- Word 图片、页眉、页脚和文本框
- 加密或受密码保护的文件处理
- 精确 Token 切分
- 文档唯一 ID、版本和权限元数据

---

## 九、学习结论

- PDF 是固定版式，适合按页解析并保存页码。
- Word 是流式排版，适合按段落和表格等逻辑结构解析。
- 提取到全部内容不等于保留了正确结构，段落与表格必须按原始顺序处理。
- 不同文件格式应通过独立解析器实现，再统一转换为 LangChain `Document`。
- 批量任务必须隔离单文件异常，并输出可追踪的处理报告。
- 文档解析、文本切分、Embedding 和向量入库构成 RAG 的数据准备链路。

**掌握程度：★★★★☆**

尚未达到五星的原因：当前完成了电子 PDF、Word 和批量处理，但尚未实现 OCR、复杂版面解析和生产级元数据管理。

---

*最后更新：2026年7月13日*
