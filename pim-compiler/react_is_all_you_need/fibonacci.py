def fibonacci(n):
    """
    计算斐波那契数列的前n项
    
    Args:
        n (int): 要计算的斐波那契数列项数
        
    Returns:
        list: 包含前n项斐波那契数的列表
        
    Raises:
        ValueError: 如果n不是正整数
    """
    # 输入验证
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n必须是正整数")
    
    # 处理特殊情况
    if n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    # 计算斐波那契数列
    fib_sequence = [0, 1]
    for i in range(2, n):
        next_num = fib_sequence[i-1] + fib_sequence[i-2]
        fib_sequence.append(next_num)
    
    return fib_sequence


# 测试函数
if __name__ == "__main__":
    # 测试各种情况
    print("斐波那契数列前10项:", fibonacci(10))
    print("斐波那契数列前5项:", fibonacci(5))
    print("斐波那契数列前1项:", fibonacci(1))
    
    # 测试错误输入
    try:
        fibonacci(0)
    except ValueError as e:
        print(f"错误测试 - 输入0: {e}")
    
    try:
        fibonacci(-5)
    except ValueError as e:
        print(f"错误测试 - 输入负数: {e}")
    
    try:
        fibonacci("abc")
    except ValueError as e:
        print(f"错误测试 - 输入字符串: {e}")