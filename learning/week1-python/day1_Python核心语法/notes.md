# Day 1 - Python核心语法

## 学习时间
2026年5月30日

## 学习目标
- 掌握Python核心语法
- 理解变量、字符串、列表、字典
- 掌握控制流、循环、函数、文件读写

---

## 一、变量和数据类型

### 1. 变量定义
```python
# Python 不需要声明类型
name = "张三"      # 字符串
age = 25          # 整数
pi = 3.14         # 浮点数
is_student = True  # 布尔值
```

### 2. 变量命名规则
- 只能包含字母、数字、下划线
- 不能以数字开头
- 区分大小写
- 不能使用关键字（如 if、for、while）

---

## 二、字符串

### 1. 字符串操作
```python
name = "Hello, Python"

# 索引
print(name[0])    # H
print(name[-1])   # n

# 切片
print(name[0:5])  # Hello

# 长度
print(len(name))  # 13

# 拼接
greeting = "Hello" + " " + "Python"

# 格式化
message = f"你好，{name}"
```

### 2. 常用方法
```python
text = "  Hello, World  "

print(text.strip())      # 去除两端空格
print(text.lower())      # 转小写
print(text.upper())      # 转大写
print(text.replace("World", "Python"))  # 替换
print(text.split(","))   # 分割
```

---

## 三、列表（List）

### 1. 列表操作
```python
fruits = ["apple", "banana", "cherry"]

# 索引
print(fruits[0])     # apple
print(fruits[-1])    # cherry

# 切片
print(fruits[0:2])   # ['apple', 'banana']

# 长度
print(len(fruits))   # 3
```

### 2. 增删改
```python
fruits = ["apple", "banana", "cherry"]

# 增加
fruits.append("orange")        # 末尾追加
fruits.insert(1, "grape")     # 指定位置插入

# 删除
fruits.remove("banana")       # 按值删除
fruits.pop()                  # 删除最后一个
fruits.pop(0)                 # 删除指定索引

# 修改
fruits[0] = "mango"           # 修改指定位置
```

### 3. 遍历
```python
fruits = ["apple", "banana", "cherry"]

# 方式1：直接遍历
for fruit in fruits:
    print(fruit)

# 方式2：带索引遍历
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# 方式3：enumerate（推荐）
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
```

---

## 四、字典（Dictionary）

### 1. 字典操作
```python
person = {
    "name": "张三",
    "age": 25,
    "city": "北京"
}

# 访问
print(person["name"])           # 张三
print(person.get("phone", "未设置"))  # 未设置

# 修改
person["age"] = 26
person["phone"] = "13800138000"

# 删除
del person["age"]
person.pop("name")
```

### 2. 遍历
```python
person = {"name": "张三", "age": 25}

# 遍历 key
for key in person.keys():
    print(key)

# 遍历 value
for value in person.values():
    print(value)

# 遍历 key-value
for key, value in person.items():
    print(f"{key}: {value}")
```

### 3. 判断 key 是否存在
```python
person = {"name": "张三", "age": 25}

print("name" in person)   # True
print("phone" in person)  # False
```

---

## 五、控制流

### 1. if 语句
```python
age = 20

if age >= 18:
    print("成年")
elif age >= 12:
    print("青少年")
else:
    print("儿童")
```

### 2. 三元表达式
```python
age = 20
status = "成年" if age >= 18 else "未成年"
```

---

## 六、循环

### 1. for 循环
```python
# 遍历列表
for i in [1, 2, 3]:
    print(i)

# 遍历范围
for i in range(5):      # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):   # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):  # 0, 2, 4, 6, 8
    print(i)
```

### 2. while 循环
```python
count = 0
while count < 5:
    print(count)
    count += 1
```

### 3. break 和 continue
```python
# break：跳出循环
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue：跳过本次循环
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # 1, 3, 5, 7, 9
```

---

## 七、函数

### 1. 基本定义
```python
def greet(name):
    print(f"你好，{name}")

greet("张三")  # 调用
```

### 2. 默认参数
```python
def greet(name, message="你好"):
    print(f"{message}，{name}")

greet("张三")           # 你好，张三
greet("张三", "早上好")  # 早上好，张三
```

### 3. 返回值
```python
def add(a, b):
    return a + b

result = add(3, 5)  # result = 8
```

### 4. 可变参数
```python
# *args：可变位置参数（元组）
def calculate(*args):
    total = 0
    for num in args:
        total += num
    return total

calculate(1, 2, 3)    # 6
calculate(1, 2, 3, 4) # 10

# **kwargs：可变关键字参数（字典）
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="张三", age=25)
```

---

## 八、文件读写

### 1. 写入文件
```python
# w：写入（覆盖）
with open("test.txt", "w") as f:
    f.write("Hello, Python!\n")
    f.write("第二行\n")

# a：追加
with open("test.txt", "a") as f:
    f.write("追加的内容\n")
```

### 2. 读取文件
```python
# r：读取
with open("test.txt", "r") as f:
    content = f.read()        # 读取全部内容
    lines = f.readlines()     # 读取所有行（列表）
    line = f.readline()       # 读取一行
```

### 3. with 语句
- 自动关闭文件
- 即使出现异常也会关闭
- 推荐使用

---

## 九、关键概念对比

### Python vs Java

| 概念 | Python | Java |
|------|--------|------|
| 变量声明 | 不需要类型 | 必须声明类型 |
| 字符串 | `str` | `String` |
| 列表 | `list` | `ArrayList` |
| 字典 | `dict` | `HashMap` |
| 循环 | `for x in list` | `for (Type x : list)` |
| 函数 | `def func():` | `public void func()` |
| 文件操作 | `with open()` | `try-with-resources` |

---

## 十、练习题

### 练习1：变量和字符串
```python
name = "张三"
age = 25
message = f"我叫{name}，今年{age}岁"
print(message)
```

### 练习2：列表操作
```python
numbers = [1, 2, 3, 4, 5]
even_numbers = [x for x in numbers if x % 2 == 0]
print(even_numbers)  # [2, 4]
```

### 练习3：字典操作
```python
student = {"name": "李四", "score": 85}
if student["score"] >= 60:
    print(f"{student['name']}及格")
else:
    print(f"{student['name']}不及格")
```

---

## 十一、学习心得

- Python 语法简洁，不需要声明变量类型
- 列表和字典是最常用的数据结构
- `with` 语句让文件操作更安全
- 函数支持默认参数和可变参数
- 列表推导式是 Python 的特色

---

## 十二、待复习内容

- [ ] 变量命名规则
- [ ] 字符串格式化
- [ ] 列表增删改查
- [ ] 字典遍历方式
- [ ] for 循环和 while 循环
- [ ] 函数定义和调用
- [ ] 文件读写操作

---

*笔记创建时间：2026年5月30日*
*学习时长：2小时*
*掌握程度：★★★★☆*
