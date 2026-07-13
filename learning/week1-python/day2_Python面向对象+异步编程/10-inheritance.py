# 10 - 继承
# 面向对象编程的核心概念

# ============================================
# 1. 基础继承
# ============================================

# 父类（基类）
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        print(f"{self.name}发出声音")

# 子类（派生类）继承父类
class Dog(Animal):
    # 子类可以有自己的方法
    def bark(self):
        print(f"{self.name}说：汪汪汪！")

class Cat(Animal):
    def meow(self):
        print(f"{self.name}说：喵喵喵~")

# 创建对象
dog = Dog("旺财")
cat = Cat("咪咪")

# 调用父类的方法（继承来的）
dog.speak()  # 旺财发出声音
cat.speak()  # 咪咪发出声音

# 调用子类自己的方法
dog.bark()   # 旺财说：汪汪汪！
cat.meow()   # 咪咪说：喵喵喵~

# ============================================
# 2. 方法重写（Override）
# ============================================

class Bird(Animal):
    # 重写父类的 speak 方法
    def speak(self):
        print(f"{self.name}说：叽叽喳喳~")

bird = Bird("小鸟")
bird.speak()  # 小鸟说：叽叽喳喳~（调用的是重写后的方法）

# ============================================
# 3. super() 调用父类方法
# ============================================

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def info(self):
        print(f"姓名：{self.name}，年龄：{self.age}")

class Student(Person):
    def __init__(self, name, age, school):
        # 调用父类的 __init__ 方法
        super().__init__(name, age)
        self.school = school

    # 重写 info 方法，但保留父类的部分
    def info(self):
        super().info()  # 调用父类的 info
        print(f"学校：{self.school}")

stu = Student("张三", 20, "北京大学")
stu.info()
# 输出：
# 姓名：张三，年龄：20
# 学校：北京大学

# ============================================
# 4. 多重继承
# ============================================

class Flyable:
    def fly(self):
        print("我会飞")

class Swimmable:
    def swim(self):
        print("我会游泳")

# 多重继承：同时继承两个类
class Duck(Animal, Flyable, Swimmable):
    pass

duck = Duck("唐老鸭")
duck.speak()  # 唐老鸭发出声音（继承 Animal）
duck.fly()    # 我会飞（继承 Flyable）
duck.swim()   # 我会游泳（继承 Swimmable）

# ============================================
# 5. 练习
# ============================================

# 练习1：定义一个"形状类" Shape
# - 属性：color（颜色）
# - 方法：area() 返回面积

class Shape:
    def __init__(self, color):
        self.color = color

    def area(self):
        return 0

# 练习2：定义"圆形类" Circle 继承 Shape
# - 属性：radius（半径）
# - 方法：area() 返回圆的面积

import math

class Circle(Shape):
    def __init__(self, color, radius):
        super().__init__(color)
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

# 练习3：定义"矩形类" Rectangle 继承 Shape
# - 属性：width（宽）、height（高）
# - 方法：area() 返回矩形的面积

class Rectangle(Shape):
    def __init__(self, color, width, height):
        super().__init__(color)
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

# 测试
circle = Circle("红色", 5)
rect = Rectangle("蓝色", 4, 6)

print(f"圆形面积：{circle.area():.2f}")  # 圆形面积：78.54
print(f"矩形面积：{rect.area()}")        # 矩形面积：24
print(f"圆形颜色：{circle.color}")        # 圆形颜色：红色
