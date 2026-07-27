# 09 - 类和对象基础
# Python面向对象编程（OOP）

# ============================================
# 1. 类的定义
# ============================================

# 定义一个"学生类"
class Student:
    # 类属性（所有对象共享）
    school = "北京大学"

    # __init__ 方法：初始化对象的属性
    # 当创建对象时自动调用
    def __init__(self, name, age):
        self.name = name  # 实例属性
        self.age = age    # 实例属性

# 创建对象（实例化）
stu1 = Student("张三", 20)
stu2 = Student("李四", 22)

print(stu1.name)  # 张三
print(stu2.age)   # 22
print(Student.school)  # 北京大学
print(stu1.school)     # 北京大学（对象也可以访问类属性）

# ============================================
# 2. 方法
# ============================================

class Dog:
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed

    # 实例方法：第一个参数是 self
    def bark(self):
        print(f"{self.name}说：汪汪汪！")

    def info(self):
        print(f"名字：{self.name}，品种：{self.breed}")

# 创建对象
dog1 = Dog("旺财", "金毛")
dog2 = Dog("小黑", "拉布拉多")

# 调用方法
dog1.bark()    # 旺财说：汪汪汪！
dog2.info()    # 名字：小黑，品种：拉布拉多

# ============================================
# 3. self 是什么？
# ============================================

# self 代表当前对象自己
# 调用 dog1.bark() 时，self = dog1
# 调用 dog2.bark() 时，self = dog2

class Cat:
    def __init__(self, name):
        self.name = name

    def meow(self):
        # self.name 就是当前这只猫的名字
        print(f"{self.name}说：喵喵喵~")

cat1 = Cat("咪咪")
cat2 = Cat("花花")

cat1.meow()  # 咪咪说：喵喵喵~
cat2.meow()  # 花花说：喵喵喵~

# ============================================
# 4. 练习
# ============================================

# 练习1：定义一个"银行账户类"
# 属性：owner（户主）、balance（余额）
# 方法：deposit(amount) 存钱、withdraw(amount) 取钱

class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print(f"存入{amount}元，余额：{self.balance}元")

    def withdraw(self, amount):
        if amount > self.balance:
            print("余额不足！")
        else:
            self.balance -= amount
            print(f"取出{amount}元，余额：{self.balance}元")

    def info(self):
        print(f"户主：{self.owner}，余额：{self.balance}元")

# 测试
account = BankAccount("张三", 1000)
account.deposit(500)     # 存入500元，余额：1500元
account.withdraw(200)    # 取出200元，余额：1300元
account.withdraw(2000)   # 余额不足！
account.info()           # 户主：张三，余额：1300元
