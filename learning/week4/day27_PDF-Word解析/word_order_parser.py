from pathlib import Path

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph
from langchain_core.documents import Document as LangChainDocument


def iter_blocks(document):
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


word_path = Path(__file__).parent / "sample_contract.docx"
document = Document(word_path)

records = []

for block_index, block in enumerate(iter_blocks(document), start=1):
    if isinstance(block, Paragraph):
        text = block.text.strip()

        if not text:
            continue

        records.append({
            "content": text,
            "metadata": {
                "source": word_path.name,
                "file_type": "docx",
                "block_type": "paragraph",
                "block_index": block_index,
                "style": block.style.name,
            },
        })

    elif isinstance(block, Table):
        table_rows = []

        for row in block.rows:
            cell_values = [
                cell.text.strip()
                for cell in row.cells
            ]

            if any(cell_values):
                table_rows.append(" | ".join(cell_values))

        if table_rows:
            records.append({
                "content": "\n".join(table_rows),
                "metadata": {
                    "source": word_path.name,
                    "file_type": "docx",
                    "block_type": "table",
                    "block_index": block_index,
                },
            })

for record in records:
    print(record)


langchain_documents = [
    LangChainDocument(
        page_content=record["content"],
        metadata=record["metadata"],
    )
    for record in records
]

print("\nLangChain Document 数量：", len(langchain_documents))
print("第一条正文：", langchain_documents[0].page_content)
print("第一条元数据：", langchain_documents[0].metadata)
print("第一条对象类型：", type(langchain_documents[0]))
