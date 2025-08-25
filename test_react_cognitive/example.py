# 计数器使用示例

# 导入计数器模块
import counter

def main():
    print("=== 计数器模块使用示例 ===")
    
    # 使用全局计数器函数
    print("\n1. 使用全局计数器函数:")
    print(f"初始值: {counter.get_value()}")
    print(f"增加1后: {counter.increment()}")
    print(f"再增加3后: {counter.increment(3)}")
    print(f"减少2后: {counter.decrement(2)}")
    print(f"重置为10: {counter.reset(10)}")
    print(f"当前值: {counter.get_value()}")
    
    # 使用Counter类
    print("\n2. 使用Counter类:")
    my_counter = counter.Counter(5)
    print(f"创建计数器，初始值为5: {my_counter.get_value()}")
    print(f"增加1后: {my_counter.increment()}")
    print(f"减少3后: {my_counter.decrement(3)}")
    print(f"重置为0: {my_counter.reset()}")
    print(f"当前值: {my_counter.get_value()}")
    
    # 多个独立计数器
    print("\n3. 多个独立计数器:")
    counter1 = counter.Counter()
    counter2 = counter.Counter(100)
    
    print(f"计数器1初始值: {counter1.get_value()}")
    print(f"计数器2初始值: {counter2.get_value()}")
    
    counter1.increment(5)
    counter2.decrement(10)
    
    print(f"计数器1增加5后: {counter1.get_value()}")
    print(f"计数器2减少10后: {counter2.get_value()}")
    
    # 全局计数器不受影响
    print(f"\n全局计数器当前值: {counter.get_value()}")

if __name__ == "__main__":
    main()