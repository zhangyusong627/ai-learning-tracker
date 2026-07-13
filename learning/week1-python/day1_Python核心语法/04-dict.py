# ===== 字典（Dict）= Java 的 HashMap =====

# 创建
person = {
    "name": "张三",
    "age": 25,
    "skills": ["Python", "Java"]
}

# 访问
print(person["name"])              # "张三"
print(person.get("email", "无"))   # 不存在返回默认值

# 修改
person["age"] = 26
person["email"] = "test@example.com"  # 不存在则新增

# 删除
del person["email"]               # 删除键
# person.pop("age")               # 删除并返回值

# 遍历
for key in person:
    print(f"{key}: {person[key]}")

# 推荐方式
for key, value in person.items():
    print(f"{key}: {value}")

# 只遍历 key 或 value
print(person.keys())    # dict_keys(['name', 'age', 'skills'])
print(person.values())  # dict_values(['张三', 26, ['Python', 'Java']])

# 判断 key 是否存在
if "name" in person:
    print("存在 name 键")

# 嵌套字典
students = {
    "张三": {"age": 25, "score": 90},
    "李四": {"age": 23, "score": 85}
}

for name, info in students.items():
    print(f"{name}: {info['age']}岁, {info['score']}分")

# 字典推导式
scores = {"张三": 90, "李四": 80, "王五": 95}
passed = {k: v for k, v in scores.items() if v >= 85}
print(passed)  # {'张三': 90, '王五': 95}
