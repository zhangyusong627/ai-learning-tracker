# Day 2 - Python面向对象+异步编程

## 学习时间
2026年5月31日

## 学习目标
- 掌握Python面向对象编程（OOP）
- 理解异步编程（async/await）

---

## 一、面向对象编程（OOP）

### 1. 类和对象

**核心概念**：
- **类（Class）**：抽象模板，定义属性和行为
- **对象（Object）**：类的具体实例

**Python vs Java 对比**：

```python
# Python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

stu = Student("张三", 20)
```

```java
// Java
public class Student {
    private String name;
    private int age;

    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }
}

Student stu = new Student("张三", 20);
```

**关键区别**：
- Python 不需要声明属性类型，直接赋值自动创建
- Python 的 `__init__` 相当于 Java 的构造方法
- Python 的 `self` 相当于 Java 的 `this`

### 2. 类属性 vs 实例属性

```python
class Student:
    school = "北京大学"  # 类属性（所有对象共享）

    def __init__(self, name):
        self.name = name  # 实例属性（对象私有）
```

- **类属性**：所有对象共享，通过类名或对象访问
- **实例属性**：每个对象独有，只能通过对象访问

### 3. 方法和 self

```python
class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):  # self 代表当前对象
        print(f"{self.name}说：汪汪汪！")

dog = Dog("旺财")
dog.bark()  # Python 会转换成 Dog.bark(dog)
```

**self 的作用**：
- 代表当前对象自己
- 调用 `dog.bark()` 时，`self = dog`
- 通过 `self` 访问对象的属性和方法

### 4. 继承

```python
# 父类
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        print(f"{self.name}发出声音")

# 子类继承父类
class Dog(Animal):
    def bark(self):
        print(f"{self.name}说：汪汪汪！")

dog = Dog("旺财")
dog.speak()  # 继承父类的方法
dog.bark()   # 子类自己的方法
```

**继承的作用**：
- 子类继承父类的所有非私有方法和属性
- 子类可以有自己的独特方法
- 代码复用，避免重复定义

### 5. 方法重写（Override）

```python
class Bird(Animal):
    def speak(self):  # 重写父类方法
        print(f"{self.name}说：叽叽喳喳~")

bird = Bird("小鸟")
bird.speak()  # 输出：小鸟说：叽叽喳喳~（不是"发出声音"）
```

**什么时候重写**：
- 当父类的方法无法满足子类的需求时
- 子类需要独特的行为

### 6. super() 调用父类方法

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def info(self):
        print(f"姓名：{self.name}，年龄：{self.age}")

class Student(Person):
    def __init__(self, name, age, school):
        super().__init__(name, age)  # 调用父类的 __init__
        self.school = school

    def info(self):
        super().info()  # 调用父类的 info
        print(f"学校：{self.school}")
```

**super() 的作用**：
- 调用父类的方法
- 避免重复代码
- 保持父类逻辑的完整性

### 7. 多态

```python
class Shape:
    def area(self):
        return 0

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

# 同一个方法名，不同实现
circle = Circle(5)
rect = Rectangle(4, 6)

print(circle.area())  # 78.5
print(rect.area())    # 24
```

**多态的核心**：
- 同一个接口（方法名），不同的实现
- 子类可以重写父类方法，实现自己的逻辑

---

## 二、异步编程（async/await）

### 1. 同步 vs 异步

**同步（Synchronous）**：
```
洗衣服（30分钟）→ 煮饭（20分钟）→ 扫地（10分钟）
总耗时：60分钟
```

**异步（Asynchronous）**：
```
同时进行：洗衣服、煮饭、扫地
总耗时：30分钟（取最长时间）
```

**核心区别**：
- **同步**：必须等待一个任务完成，才能开始下一个
- **异步**：多个任务可以同时进行，不用傻等

### 2. 协程（Coroutine）

```python
import asyncio

# 定义协程函数（用 async 修饰）
async def say_hello():
    print("Hello")
    await asyncio.sleep(1)  # 异步等待1秒
    print("World")

# 运行协程
asyncio.run(say_hello())
```

**关键概念**：
- `async def`：定义异步函数（协程）
- `await`：暂停当前任务，等待结果
- `asyncio.run()`：启动事件循环，运行协程

### 3. asyncio.sleep() vs time.sleep()

```python
import asyncio
import time

# time.sleep() - 同步等待，阻塞程序
time.sleep(2)  # 程序停顿2秒，不能做其他事

# asyncio.sleep() - 异步等待，不阻塞
await asyncio.sleep(2)  # 等待2秒，但可以同时处理其他任务
```

### 4. 并发执行多个任务

```python
async def download_file(filename):
    print(f"开始下载 {filename}")
    await asyncio.sleep(2)  # 模拟下载耗时2秒
    print(f"{filename} 下载完成")
    return filename

async def download_all():
    files = ["video.mp4", "image.jpg", "document.pdf"]
    tasks = [download_file(f) for f in files]
    results = await asyncio.gather(*tasks)  # 并发执行
    print(f"所有文件下载完成：{results}")

asyncio.run(download_all())
```

**输出顺序**：
```
开始下载 video.mp4
开始下载 image.jpg
开始下载 document.pdf
image.jpg 下载完成
video.mp4 下载完成
document.pdf 下载完成
所有文件下载完成：['video.mp4', 'image.jpg', 'document.pdf']
```

**总耗时**：2秒（不是6秒，因为同时下载）

### 5. asyncio.gather() 的作用

```python
# 同时执行多个异步任务
await asyncio.gather(
    task1(),
    task2(),
    task3(),
)
```

**特点**：
- 所有任务同时开始
- 等待所有任务完成
- 返回所有任务的结果列表

### 6. 什么时候用异步？

**适合异步的场景**：
- Web服务器同时处理多个用户请求
- 同时下载多个文件
- 爬虫同时抓取多个网页
- 同时执行多个数据库查询

**不适合异步的场景**：
- 银行转账（A扣钱 → B加钱，必须串行）
- 下单流程（验证库存 → 扣减库存 → 生成订单，有依赖）
- 文件读写（先读取 → 处理 → 写入，有顺序）

---

## 三、Python vs Java 对比总结

| 特性 | Python | Java |
|------|--------|------|
| 类定义 | `class Animal:` | `public class Animal {}` |
| 构造方法 | `def __init__(self, name):` | `public Animal(String name)` |
| 属性赋值 | `self.name = name` | `this.name = name` |
| 继承 | `class Dog(Animal):` | `class Dog extends Animal` |
| 调用父类 | `super().__init__(name)` | `super(name)` |
| 方法重写 | 直接重写方法 | `@Override` 注解 |
| 异步编程 | `async/await` | `CompletableFuture` |
| 类型声明 | 不需要 | 必须声明类型 |

---

## 四、关键代码速查

### 类和对象
```python
class MyClass:
    class_attr = "类属性"

    def __init__(self, value):
        self.instance_attr = value

    def my_method(self):
        return self.instance_attr

obj = MyClass("hello")
print(obj.class_attr)      # 类属性
print(obj.instance_attr)   # 实例属性
obj.my_method()            # 调用方法
```

### 继承
```python
class Parent:
    def parent_method(self):
        print("父类方法")

class Child(Parent):
    def child_method(self):
        print("子类方法")

    def parent_method(self):  # 重写
        super().parent_method()  # 调用父类
        print("重写后的方法")

child = Child()
child.parent_method()
```

### 异步编程
```python
import asyncio

async def async_task(name, delay):
    print(f"任务 {name} 开始")
    await asyncio.sleep(delay)
    print(f"任务 {name} 完成")

async def main():
    # 并发执行多个任务
    await asyncio.gather(
        async_task("A", 2),
        async_task("B", 1),
        async_task("C", 3),
    )

asyncio.run(main())
```

---

## 五、练习题

### 练习1：定义一个"动物类"
```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        print(f"{self.name}发出声音")

class Dog(Animal):
    def speak(self):
        print("汪汪汪！")

dog = Dog("旺财")
dog.speak()  # 输出：汪汪汪！
```

### 练习2：异步下载文件
```python
import asyncio

async def download_file(filename):
    print(f"开始下载 {filename}")
    await asyncio.sleep(2)
    print(f"{filename} 下载完成")
    return filename

async def download_all():
    files = ["file1.txt", "file2.txt", "file3.txt"]
    tasks = [download_file(f) for f in files]
    results = await asyncio.gather(*tasks)
    print(f"所有文件下载完成：{results}")

asyncio.run(download_all())
# 总耗时：2秒（不是6秒）
```

---

## 六、学习心得

- Python 的类比 Java 更简洁，不需要声明属性类型
- `self` 类似 Java 的 `this`，但必须显式写出来
- 继承和多态的概念与 Java 类似
- 异步编程是 Python 的强大特性，Java 没有直接对应
- `async/await` 让异步代码看起来像同步，更易读
- `asyncio.gather()` 可以轻松实现并发执行

---

## 七、待复习内容

- [ ] 类属性 vs 实例属性的区别
- [ ] `self` 的作用和用法
- [ ] 继承和方法重写
- [ ] `super()` 的使用场景
- [ ] `async/await` 的基本用法
- [ ] `asyncio.gather()` 的并发执行

---

## 八、下一步学习

- [ ] 周三：FastAPI基础
- [ ] 实践：用 FastAPI 搭建简单的API
- [ ] 理解请求响应机制

---

*笔记创建时间：2026年5月31日*
*学习时长：2小时*
*掌握程度：★★★★☆*
