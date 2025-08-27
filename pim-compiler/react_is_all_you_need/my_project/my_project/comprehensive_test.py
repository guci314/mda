#!/usr/bin/env python3
from calculator import Calculator

def test_comprehensive():
    """综合测试计算器的所有功能"""
    calc = Calculator()
    
    print("🧪 开始综合测试计算器...")
    
    # 测试加法
    assert calc.add(2, 3) == 5, "加法测试失败"
    assert calc.add(-1, 1) == 0, "负数加法测试失败"
    assert calc.add(2.5, 3.5) == 6.0, "小数加法测试失败"
    print("✅ 加法测试通过")
    
    # 测试减法
    assert calc.subtract(5, 3) == 2, "减法测试失败"
    assert calc.subtract(0, 5) == -5, "负数减法测试失败"
    assert calc.subtract(5.5, 2.5) == 3.0, "小数减法测试失败"
    print("✅ 减法测试通过")
    
    # 测试乘法
    assert calc.multiply(2, 3) == 6, "乘法测试失败"
    assert calc.multiply(-2, 3) == -6, "负数乘法测试失败"
    assert calc.multiply(2.5, 4) == 10.0, "小数乘法测试失败"
    print("✅ 乘法测试通过")
    
    # 测试除法
    assert calc.divide(6, 3) == 2, "除法测试失败"
    assert calc.divide(10, 2) == 5, "除法测试失败"
    assert calc.divide(1, 2) == 0.5, "小数除法测试失败"
    assert calc.divide(5.0, 2) == 2.5, "浮点数除法测试失败"
    print("✅ 除法测试通过")
    
    # 测试除零异常
    try:
        calc.divide(5, 0)
        assert False, "除零异常测试失败 - 应该抛出异常"
    except ValueError as e:
        assert str(e) == "除数不能为零", f"异常消息不正确: {e}"
    
    try:
        calc.divide(0, 0)
        assert False, "0除以0异常测试失败 - 应该抛出异常"
    except ValueError as e:
        assert str(e) == "除数不能为零", f"异常消息不正确: {e}"
    print("✅ 除零异常测试通过")
    
    print("\n🎉 所有综合测试通过! 计算器功能正常。")

if __name__ == "__main__":
    test_comprehensive()