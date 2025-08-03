import unittest
from utils import format_date

class TestFormatDate(unittest.TestCase):
    def test_default_format(self):
        """测试默认输入和输出格式"""
        self.assertEqual(format_date("2023-10-05"), "05/10/2023")

    def test_custom_format(self):
        """测试自定义输入和输出格式"""
        self.assertEqual(format_date("05-10-2023", "%d-%m-%Y", "%Y/%m/%d"), "2023/10/05")

    def test_invalid_date(self):
        """测试无效日期格式"""
        with self.assertRaises(ValueError):
            format_date("invalid-date")

if __name__ == "__main__":
    unittest.main()