#!/usr/bin/env python3
"""
费曼学习法 - LangChain Memory 机制
====================================
核心概念：Memory 就是一个"笔记本"，记录历史对话
"""

# ===== 第1步：体验"没有记忆"的 AI =====
# 先理解问题，才能理解解决方案

print("=" * 50)
print("第1步：体验没有记忆的 AI")
print("=" * 50)

# 模拟一个简单的 AI（没有记忆）
def simple_ai(user_input):
    """模拟 AI，每次都是独立调用，不记得之前说过什么"""
    responses = {
        "你好": "你好！有什么可以帮你的？",
        "我叫小明": "很高兴认识你，小明！",
    }
    return responses.get(user_input, "我不太理解你的意思")

# 两次对话
print(f"你：我叫小明")
print(f"AI：{simple_ai('我叫小明')}")

print(f"\n你：我叫什么？")
print(f"AI：{simple_ai('我叫什么？')}")  # AI 不记得了！
print("\n→ AI 完全不知道你叫什么，因为它没有记忆！\n")


# ===== 第2步：手动实现一个"笔记本" =====
print("=" * 50)
print("第2步：手动实现 Memory（笔记本）")
print("=" * 50)

# 创建一个笔记本
memory = []

def ai_with_memory(user_input):
    """带记忆的 AI"""
    # 简单逻辑：如果问"我叫什么"，就从历史里找
    if "叫什么" in user_input or "我是谁" in user_input:
        for msg in memory:
            if msg['role'] == 'user' and '我叫' in msg['content']:
                name = msg['content'].replace('我叫', '').strip()
                return f"你叫{name}呀！"

    # 记录到笔记本
    memory.append({"role": "user", "content": user_input})

    response = f"收到：{user_input}"
    memory.append({"role": "assistant", "content": response})
    return response

# 测试带记忆的 AI
print("你：我叫小明")
print(f"AI：{ai_with_memory('我叫小明')}")

print(f"\n你：我叫什么？")
print(f"AI：{ai_with_memory('我叫什么？')}")  # 记住了！
print("\n→ 这次 AI 记住了！因为我们用了笔记本（memory 列表）\n")


# ===== 第3步：思考题 =====
print("=" * 50)
print("第3步：思考")
print("=" * 50)
print("""
我们刚才手动实现了 Memory，本质就是：
1. 创建一个列表 memory = []
2. 每次对话都追加进去
3. 需要时从里面查找历史

但 LangChain 已经帮我们封装好了各种 Memory 类型，
接下来我们要学习的就是：
- ConversationBufferMemory（完整记录）
- ConversationSummaryMemory（自动总结）
- ConversationBufferWindowMemory（只保留最近几轮）

你觉得这三种分别适合什么场景？
""")

# 等待用户思考后，再进入下一步
input("思考完后按回车继续...")
print("\n很好！接下来我们用 LangChain 的 ConversationBufferMemory 实现相同的效果。")
print("请运行: python 02_buffer_memory.py")
