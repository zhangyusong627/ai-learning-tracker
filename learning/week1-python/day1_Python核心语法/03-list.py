# ===== 列表（List）= Java 的 ArrayList =====

# 创建
fruits = ["苹果", "香蕉", "橘子"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]  # 可以混合类型

# 访问
print(fruits[0])      # "苹果"
print(fruits[-1])     # "橘子"（倒数第一个）

# 修改
fruits[0] = "草莓"

# 添加
fruits.append("葡萄")       # 末尾添加
fruits.insert(1, "西瓜")    # 指定位置插入

# 删除
fruits.remove("香蕉")       # 按值删除
fruits.pop()                # 弹出最后一个
# fruits.clear()            # 清空列表

# 遍历
for fruit in fruits:
    print(fruit)

# 带索引遍历
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# enumerate（推荐）
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

# 切片（Python 特色）
nums = [0, 1, 2, 3, 4, 5]
print(nums[1:4])     # [1, 2, 3]
print(nums[:3])      # [0, 1, 2]
print(nums[3:])      # [3, 4, 5]
print(nums[::2])     # [0, 2, 4] 步长2

# 排序
nums = [3, 1, 4, 1, 5, 9]
nums.sort()          # 原地排序
print(nums)          # [1, 1, 3, 4, 5, 9]

sorted_nums = sorted(nums, reverse=True)  # 返回新列表
print(sorted_nums)   # [9, 5, 4, 3, 1, 1]

# 常用函数
print(len([1, 2, 3]))       # 3
print(max([1, 2, 3]))       # 3
print(min([1, 2, 3]))       # 1
print(sum([1, 2, 3]))       # 6
