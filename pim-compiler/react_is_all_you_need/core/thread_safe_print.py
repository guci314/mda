"""
线程安全的打印工具
"""
import threading
import sys

print_lock = threading.Lock()

def safe_print(*args, **kwargs):
    """线程安全的print"""
    with print_lock:
        print(*args, **kwargs)
        sys.stdout.flush()

# 替换全局print
import builtins
builtins._original_print = builtins.print
builtins.print = safe_print