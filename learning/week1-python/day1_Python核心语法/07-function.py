# ===== 函数 =====

# 基本定义
def greet(name):
    print(f"你好，{name}")

greet("张三")

# 默认参数
def greet_times(name, times=1):
    for _ in range(times):
        print(f"你好，{name}")

greet_times("张三")           # 打印 1 次
greet_times("张三", times=3)  # 打印 3 次

# 返回多个值（Java 做不到）
def get_min_max(numbers):
    return min(numbers), max(numbers)

low, high = get_min_max([1, 5, 3, 9, 2])
print(f"最小: {low}, 最大: {high}")

# *args 和 **kwargs（可变参数）
def func(*args, **kwargs):
    print(f"args: {args}")       # 元组：(1, 2, 3)
    print(f"kwargs: {kwargs}")   # 字典：{'a': 1, 'b': 2}

func(1, 2, 3, a=1, b=2)

# Lambda 函数（匿名函数）
add = lambda x, y: x + y
print(add(3, 5))  # 8

# 常见高阶函数
nums = [1, 2, 3, 4, 5]

# map：对每个元素应用函数
squared = list(map(lambda x: x ** 2, nums))
print(squared)  # [1, 4, 9, 16, 25]

# filter：过滤元素
evens = list(filter(lambda x: x % 2 == 0, nums))
print(evens)  # [2, 4]

# sorted + key：自定义排序
students = [("张三", 90), ("李四", 85), ("王五", 95)]
sorted_students = sorted(students, key=lambda s: s[1], reverse=True)
print(sorted_students)  # [('王五', 95), ('张三', 90), ('李四', 85)]

# 全局变量 vs 局部变量
x = 10  # 全局变量

def func2():
    x = 20  # 局部变量，不会修改全局的 x
    print(f"函数内: {x}")

func2()
print(f"函数外: {x}")

# 如果要修改全局变量
def func3():
    global x
    x = 20

func3()
print(f"修改后: {x}")  # 20
