# ===== 条件判断 =====

age = 25

# if-elif-else（注意缩进，不用大括号）
if age < 18:
    print("未成年")
elif age < 60:
    print("成年人")
else:
    print("老年人")

# 真值判断（不需要写 == true）
is_active = True
if is_active:        # 而不是 if (is_active == true)
    print("激活")

if not is_active:
    print("未激活")

# 逻辑运算符
if age >= 18 and age < 60:
    print("劳动年龄")

if age < 18 or age >= 60:
    print("非劳动年龄")

# in 运算符
fruits = ["苹果", "香蕉", "橘子"]
if "苹果" in fruits:
    print("有苹果")

if "西瓜" not in fruits:
    print("没有西瓜")

# 三元表达式
age = 20
status = "成年" if age >= 18 else "未成年"
print(status)

# match-case（Python 3.10+，类似 Java 的 switch）
command = "start"
match command:
    case "start":
        print("启动")
    case "stop":
        print("停止")
    case _:
        print("未知命令")
