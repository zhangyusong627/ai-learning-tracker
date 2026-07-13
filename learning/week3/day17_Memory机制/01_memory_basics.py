history = []

def chat(user_input):
    # 1. 存用户输入
    history.append({"role": "user", "content": user_input})

    # 2. 生成 AI 回复（简化版）
    ai_response = f"收到：{user_input}"

    # 3. 存 AI 回复
    history.append({"role": "assistant", "content": ai_response})

    return ai_response

# 测试
print("第1轮：", chat("我叫小明"))
print("第2轮：", chat("我喜欢苹果"))

# 查看历史记录
print("\n历史记录：")
for item in history:
    print(f"  {item['role']}: {item['content']}")
