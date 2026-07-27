# ===== 字符串 =====

name = "张三"
age = 25

# 格式化（推荐 f-string）
msg = f"我叫{name}，今年{age}岁"
print(msg)

# 其他格式化方式
msg2 = "我叫{}，今年{}岁".format(name, age)
msg3 = "我叫%s，今年%d岁" % (name, age)

# 常用方法
text = "  Hello, Python!  "
print(text.strip())           # "Hello, Python!" 去除首尾空格
print(text.lower())           # "  hello, python!  "
print(text.upper())           # "  HELLO, PYTHON!  "
print(text.replace("Python", "World"))  # "  Hello, World!  "
print(len(text))              # 19

# 切片
s = "Hello, World!"
print(s[0:5])     # "Hello"（左闭右开）
print(s[7:])      # "World!"
print(s[:5])      # "Hello"
print(s[-6:])     # "World!"
print(s[::2])     # "Hlo ol!"（步长2）

# 查找
print("Hello".count("l"))      # 2
print("Hello".find("llo"))     # 2
print("Hello".startswith("He")) # True
print("Hello".endswith("lo"))   # True

# 判断
print("123".isdigit())    # True
print("abc".isalpha())    # True
print("abc123".isalnum()) # True
