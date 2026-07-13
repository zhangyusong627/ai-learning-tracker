# ===== 变量与类型 =====

# Python 不需要声明类型，自动推断
age = 25              # int
name = "张三"         # str
price = 99.9          # float
active = True         # bool（注意大写）

# 查看类型
print(type(age))      # <class 'int'>
print(type(name))     # <class 'str'>
print(type(price))    # <class 'float'>

# 类型转换
num_str = "100"
num_int = int(num_str)    # 字符串转整数
num_float = float("3.14") # 字符串转浮点数
str_num = str(25)         # 数字转字符串

print(f"{num_int} + {num_float} = {num_int + num_float}")

# 多重赋值
x, y, z = 1, 2, 3
a = b = c = 0
print(x, y, z, a, b, c)

# 交换变量（Python 特色，Java 需要临时变量）
x, y = y, x
print(f"交换后: x={x}, y={y}")
