def binary_search(arr, target):
    """
    在有序数组中执行二分查找算法。
    
    参数:
    arr (list): 已排序的数组
    target: 要查找的目标值
    
    返回:
    int: 如果找到目标值，返回其索引；否则返回-1
    
    时间复杂度: O(log n)
    空间复杂度: O(1)
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1


def test_binary_search():
    """测试二分查找函数"""
    # 测试用例1: 正常情况
    arr1 = [1, 3, 5, 7, 9, 11, 13, 15]
    assert binary_search(arr1, 7) == 3
    assert binary_search(arr1, 1) == 0
    assert binary_search(arr1, 15) == 7
    assert binary_search(arr1, 6) == -1  # 不存在
    
    # 测试用例2: 空数组
    assert binary_search([], 5) == -1
    
    # 测试用例3: 单个元素
    assert binary_search([42], 42) == 0
    assert binary_search([42], 100) == -1
    
    # 测试用例4: 偶数长度数组
    arr2 = [2, 4, 6, 8, 10, 12]
    assert binary_search(arr2, 6) == 2
    assert binary_search(arr2, 12) == 5
    assert binary_search(arr2, 1) == -1
    
    print("所有测试用例通过!")


if __name__ == "__main__":
    # 运行测试
    test_binary_search()
    
    # 示例使用
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    target = 7
    result = binary_search(numbers, target)
    
    if result != -1:
        print(f"找到目标值 {target}，索引为 {result}")
    else:
        print(f"未找到目标值 {target}")