# ===== 文件读写 =====

import os

# 获取当前目录
print(f"当前目录: {os.getcwd()}")

# ===== 写文件 =====
# with 语句自动关闭文件，类似 Java 的 try-with-resources
with open("test.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n")
    f.write("第二行\n")
    f.write("第三行\n")

print("写入完成")

# ===== 读文件 =====
# 方式1：读全部
with open("test.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print("全部内容:")
    print(content)

# 方式2：按行读，返回列表
with open("test.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    print("按行读取:")
    for line in lines:
        print(line.strip())  # strip() 去掉换行符

# 方式3：逐行读（推荐，省内存）
with open("test.txt", "r", encoding="utf-8") as f:
    print("逐行读取:")
    for line in f:
        print(line.strip())

# ===== 追加写 =====
with open("test.txt", "a", encoding="utf-8") as f:
    f.write("第四行\n")

# ===== 实用示例：读取 CSV 格式 =====
# 创建示例数据
with open("data.csv", "w", encoding="utf-8") as f:
    f.write("姓名,年龄,城市\n")
    f.write("张三,25,北京\n")
    f.write("李四,23,上海\n")
    f.write("王五,28,广州\n")

# 读取并解析
with open("data.csv", "r", encoding="utf-8") as f:
    lines = f.readlines()
    header = lines[0].strip().split(",")
    print(f"表头: {header}")

    for line in lines[1:]:
        row = line.strip().split(",")
        print(f"姓名: {row[0]}, 年龄: {row[1]}, 城市: {row[2]}")

# 清理测试文件
os.remove("test.txt")
os.remove("data.csv")
print("\n测试文件已删除")
