from pathlib import Path

import fitz
from langchain_core.documents import Document as LangChainDocument


pdf_path = (
    Path(__file__).parent.parent
    / "day25_模型微调入门"
    / "2106.09685v2.pdf"
)

pages = []

skipped_pages = []

with fitz.open(pdf_path) as document:
    for page_index, page in enumerate(document):
        text = page.get_text().strip()

        if not text:
            skipped_pages.append(page_index+1)
            continue

        page_data = {
            "content": text,
            "metadata": {
                "source": pdf_path.name,
                "page": page_index + 1,
                "file_type": "pdf",
            },
        }

        pages.append(page_data)

pdf_documents = [
    LangChainDocument(
        page_content=page["content"],
        metadata=page["metadata"],
    )
    for page in pages
]

print(f"成功提取页数：{len(pages)}")
print("第一页元数据：")
print(pages[0]["metadata"])
print(f"第一页字符数：{len(pages[0]['content'])}")
if skipped_pages:
    print(f"警告：以下页面未提取到文字：{skipped_pages}")
else:
    print("所有页面均成功提取到文字")


print(f"LangChain Document 数量：{len(pdf_documents)}")
print(f"第一条对象类型：{type(pdf_documents[0])}")
print(f"第一页元数据：{pdf_documents[0].metadata}")
