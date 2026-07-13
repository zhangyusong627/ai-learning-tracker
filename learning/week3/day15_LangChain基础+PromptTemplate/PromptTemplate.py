from langchain_core.prompts import PromptTemplate


translate_prompt = PromptTemplate(
    input_variables=["language","code"],
    template="请将以下代码翻译成{language}: \n\n{code}"
)


result = translate_prompt.invoke({
    "language":"Python",
    "code":"public int add(int a, int b) { return a + b; }"
    })

print(result.text)


explain_template = PromptTemplate(
    input_variables=["level", "code"],
    template="""你是一个编程教育专家。

请用{level}的水平解释以下代码的功能：

{code}

解释要求：
1. 先说明代码的整体功能
2. 逐行解释关键代码"""
)

result2 = explain_template.invoke({
    "level": "初学者",
    "code": "for i in range(10): print(i)"
})

print(result2.text)
