import time

def fibonacci_iterative(n):
    """迭代版本"""
    if n <= 0:
        raise ValueError("n必须是正整数")
    if n == 1:
        return 0
    elif n == 2:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n):
        a, b = b, a + b
    return b

def fibonacci_recursive_memo(n, memo=None):
    """递归记忆化版本"""
    if n <= 0:
        raise ValueError("n必须是正整数")
    if memo is None:
        memo = {}
    if n == 1:
        return 0
    elif n == 2:
        return 1
    if n in memo:
        return memo[n]
    
    result = fibonacci_recursive_memo(n-1, memo) + fibonacci_recursive_memo(n-2, memo)
    memo[n] = result
    return result

def fibonacci_recursive_simple(n):
    """简单递归版本"""
    if n <= 0:
        raise ValueError("n必须是正整数")
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        return fibonacci_recursive_simple(n-1) + fibonacci_recursive_simple(n-2)

def time_function(func, n, name):
    """测量函数执行时间"""
    start_time = time.time()
    try:
        result = func(n)
        end_time = time.time()
        print(f"{name}({n}) = {result}, 耗时: {end_time - start_time:.6f}秒")
        return end_time - start_time
    except Exception as e:
        end_time = time.time()
        print(f"{name}({n}) 错误: {e}, 耗时: {end_time - start_time:.6f}秒")
        return end_time - start_time

# 性能测试
if __name__ == "__main__":
    test_values = [5, 10, 20, 30, 35]
    
    print("斐波那契函数性能对比:")
    print("=" * 50)
    
    for n in test_values:
        print(f"\n计算第{n}个斐波那契数:")
        
        # 迭代版本
        time_iterative = time_function(fibonacci_iterative, n, "迭代")
        
        # 递归记忆化版本
        time_recursive_memo = time_function(fibonacci_recursive_memo, n, "递归记忆化")
        
        # 简单递归版本（只测试小数值）
        if n <= 20:
            time_recursive_simple = time_function(fibonacci_recursive_simple, n, "简单递归")
        else:
            print("简单递归版本跳过测试（性能太差）")
        
        print("-" * 30)