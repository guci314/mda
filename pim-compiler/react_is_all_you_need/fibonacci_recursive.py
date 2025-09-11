def fibonacci_recursive(n, memo=None):
    """
    使用递归和记忆化计算第n个斐波那契数
    
    Args:
        n (int): 要计算的斐波那契数列项位置
        memo (dict): 记忆化字典，用于存储已计算结果
        
    Returns:
        int: 第n个斐波那契数
        
    Raises:
        ValueError: 如果n不是正整数
    """
    # 输入验证
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n必须是正整数")
    
    # 初始化记忆化字典
    if memo is None:
        memo = {}
    
    # 基础情况
    if n == 1:
        return 0
    elif n == 2:
        return 1
    
    # 检查是否已经计算过
    if n in memo:
        return memo[n]
    
    # 递归计算并存储结果
    result = fibonacci_recursive(n-1, memo) + fibonacci_recursive(n-2, memo)
    memo[n] = result
    
    return result


def fibonacci_recursive_simple(n):
    """
    简单的递归版本（无记忆化，性能较差）
    """
    if n <= 0:
        raise ValueError("n必须是正整数")
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        return fibonacci_recursive_simple(n-1) + fibonacci_recursive_simple(n-2)


# 测试函数
if __name__ == "__main__":
    # 测试记忆化版本
    print("使用记忆化的递归版本:")
    for i in range(1, 11):
        print(f"fibonacci_recursive({i}) = {fibonacci_recursive(i)}")
    
    print("\n简单递归版本（性能较差）:")
    for i in range(1, 11):
        print(f"fibonacci_recursive_simple({i}) = {fibonacci_recursive_simple(i)}")
    
    # 测试大数（记忆化版本可以处理）
    print(f"\n第30个斐波那契数（记忆化）: {fibonacci_recursive(30)}")
    
    # 错误测试
    try:
        fibonacci_recursive(0)
    except ValueError as e:
        print(f"错误测试: {e}")