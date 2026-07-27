# ===== 循环 =====

# for 循环
print("range(5):")
for i in range(5):          # 0,1,2,3,4
    print(i, end=" ")
print()

print("\nrange(1, 10, 2):")
for i in range(1, 10, 2):   # 1,3,5,7,9（步长2）
    print(i, end=" ")
print()

# 遍历列表
fruits = ["苹果", "香蕉", "橘子"]
for fruit in fruits:
    print(fruit)

# enumerate 带索引
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

# while 循环
count = 0
while count < 5:
    print(count, end=" ")
    count += 1    # 没有 count++ 语法
print()

# break 和 continue
for i in range(10):
    if i == 3:
        continue    # 跳过本次
    if i == 7:
        break       # 跳出循环
    print(i, end=" ")
print()

# for-else（Python 特色）
# else 在循环正常结束时执行，break 时不执行
for i in range(5):
    if i == 10:
        break
else:
    print("循环正常结束，没有 break")

# 列表推导式
squares = [x ** 2 for x in range(10)]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# 带条件过滤
even_squares = [x ** 2 for x in range(10) if x % 2 == 0]
print(even_squares)  # [0, 4, 16, 36, 64]
