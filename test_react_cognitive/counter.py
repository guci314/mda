class Counter:
    def __init__(self, initial_value=0):
        """
        初始化计数器
        
        Args:
            initial_value (int): 计数器的初始值，默认为0
        """
        self._value = initial_value
    
    def increment(self, step=1):
        """
        增加计数器的值
        
        Args:
            step (int): 增加的步长，默认为1
            
        Returns:
            int: 更新后的计数器值
        """
        self._value += step
        return self._value
    
    def decrement(self, step=1):
        """
        减少计数器的值
        
        Args:
            step (int): 减少的步长，默认为1
            
        Returns:
            int: 更新后的计数器值
        """
        self._value -= step
        return self._value
    
    def reset(self, value=0):
        """
        重置计数器的值
        
        Args:
            value (int): 重置后的值，默认为0
            
        Returns:
            int: 重置后的计数器值
        """
        self._value = value
        return self._value
    
    def get_value(self):
        """
        获取当前计数器的值
        
        Returns:
            int: 当前计数器的值
        """
        return self._value
    
    def __str__(self):
        """
        返回计数器值的字符串表示
        
        Returns:
            str: 计数器值的字符串表示
        """
        return str(self._value)


# 为了方便使用，创建一些全局函数
_counter = Counter()

def increment(step=1):
    """
    增加全局计数器的值
    
    Args:
        step (int): 增加的步长，默认为1
        
    Returns:
        int: 更新后的计数器值
    """
    return _counter.increment(step)

def decrement(step=1):
    """
    减少全局计数器的值
    
    Args:
        step (int): 减少的步长，默认为1
        
    Returns:
        int: 更新后的计数器值
    """
    return _counter.decrement(step)

def reset(value=0):
    """
    重置全局计数器的值
    
    Args:
        value (int): 重置后的值，默认为0
        
    Returns:
        int: 重置后的计数器值
    """
    return _counter.reset(value)

def get_value():
    """
    获取全局计数器的当前值
    
    Returns:
        int: 全局计数器的当前值
    """
    return _counter.get_value()