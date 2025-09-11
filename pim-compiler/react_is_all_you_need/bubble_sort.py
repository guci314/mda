def bubble_sort(arr):
    """
    冒泡排序算法实现
    
    参数:
    arr: 待排序的列表
    
    返回:
    排序后的列表
    """
    n = len(arr)
    
    # 遍历所有数组元素
    for i in range(n):
        # 最后i个元素已经排好序
        swapped = False
        
        for j in range(0, n - i - 1):
            # 如果当前元素大于下一个元素，则交换
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        
        # 如果这一轮没有交换，说明已经排序完成
        if not swapped:
            break
    
    return arr


def bubble_sort_optimized(arr):
    """
    优化的冒泡排序算法
    """
    n = len(arr)
    
    for i in range(n):
        # 标记是否发生交换
        swapped = False
        
        # 每次遍历减少比较范围
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                # 交换元素
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        
        # 如果没有交换，提前结束
        if not swapped:
            break
    
    return arr


# 测试用例
if __name__ == "__main__":
    # 测试数据
    test_cases = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 2, 8, 1, 9],
        [1, 2, 3, 4, 5],  # 已经排序的
        [5, 4, 3, 2, 1],  # 逆序的
        [3],  # 单个元素
        []    # 空列表
    ]
    
    print("冒泡排序测试:")
    for i, arr in enumerate(test_cases):
        original = arr.copy()
        sorted_arr = bubble_sort(arr.copy())
        print(f"测试 {i + 1}: {original} -> {sorted_arr}")
    
    print("\n优化的冒泡排序测试:")
    for i, arr in enumerate(test_cases):
        original = arr.copy()
        sorted_arr = bubble_sort_optimized(arr.copy())
        print(f"测试 {i + 1}: {original} -> {sorted_arr}")


# 性能分析
# 时间复杂度: 最好情况 O(n)，最坏情况 O(n²)，平均情况 O(n²)
# 空间复杂度: O(1) - 原地排序
# 稳定性: 稳定排序算法